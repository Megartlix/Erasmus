import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QDateEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader

class AnimalSalesApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Hayvan Satış Programı')
        self.setGeometry(100, 100, 600, 400)

        # Veritabanı bağlantısı
        self.conn = sqlite3.connect('veritabanları/hayvanlar.db')
        self.cursor = self.conn.cursor()

        # Arayüz bileşenleri
        self.layout = QVBoxLayout()

        form_layout = QFormLayout()

        # Hayvan Seçimi
        self.animal_combo = QComboBox()
        self.load_animals()
        form_layout.addRow(QLabel("Satılacak Hayvanı Seçin:"), self.animal_combo)

        # Alıcı Adı
        self.alici_ad = QLineEdit()
        form_layout.addRow(QLabel("Alıcı Adı:"), self.alici_ad)

        # Satış Tarihi
        self.satis_tarihi = QDateEdit()
        self.satis_tarihi.setDisplayFormat("yyyy-MM-dd")
        form_layout.addRow(QLabel("Satış Tarihi:"), self.satis_tarihi)

        # Satış Fiyatı
        self.satis_fiyati = QLineEdit()
        self.satis_fiyati.setPlaceholderText("Satış fiyatını girin")
        form_layout.addRow(QLabel("Satış Fiyatı:"), self.satis_fiyati)

        # Hayvan Ekle Butonu
        self.add_animal_button = QPushButton('Hayvan Ekle')
        self.add_animal_button.clicked.connect(self.add_animal)
        form_layout.addRow(self.add_animal_button)

        self.layout.addLayout(form_layout)

        # Hayvanlar Tablosu
        self.animal_table = QTableWidget()
        self.animal_table.setColumnCount(2)
        self.animal_table.setHorizontalHeaderLabels(['Küpe No', 'Satış Fiyatı'])
        header = self.animal_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.layout.addWidget(self.animal_table)

        # Satış Butonu
        self.sale_button = QPushButton('Satışı Gerçekleştir')
        self.sale_button.clicked.connect(self.handle_sale)
        self.layout.addWidget(self.sale_button)

        self.setLayout(self.layout)

        # Modern tema
        self.setStyleSheet("""
            QWidget {
                background-color: #2c2f38;
                color: #f1f1f1;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-weight: bold;
                color: #4CAF50;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #3c434d;
                border: 1px solid #4CAF50;
                color: #f1f1f1;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def load_animals(self):
        # Hayvanları veritabanından alıp ComboBox'a ekle
        self.cursor.execute("SELECT kupeno FROM hayvanlar")
        animals = self.cursor.fetchall()
        for animal in animals:
            self.animal_combo.addItem(animal[0])

    def add_animal(self):
        # Yeni hayvanı tabloya ekle
        kupeno = self.animal_combo.currentText()
        satis_fiyati = self.satis_fiyati.text()

        if not satis_fiyati.isdigit():
            QMessageBox.warning(self, "Hata", "Satış fiyatı geçerli bir rakam olmalı.")
            return

        row_position = self.animal_table.rowCount()
        self.animal_table.insertRow(row_position)
        self.animal_table.setItem(row_position, 0, QTableWidgetItem(kupeno))
        self.animal_table.setItem(row_position, 1, QTableWidgetItem(satis_fiyati))

        self.satis_fiyati.clear()

    def handle_sale(self):
        # Satış işlemini gerçekleştir
        alici_ad = self.alici_ad.text()
        satis_tarihi = self.satis_tarihi.text()

        if not alici_ad:
            QMessageBox.warning(self, "Hata", "Alıcı adı boş olamaz.")
            return

        if self.animal_table.rowCount() == 0:
            QMessageBox.warning(self, "Hata", "Satış yapılacak hayvan eklemelisiniz.")
            return

        conn_sales = sqlite3.connect('veritabanları/satis.db')
        cursor_sales = conn_sales.cursor()

        cursor_sales.execute('''
        CREATE TABLE IF NOT EXISTS satis (
            satis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kupeno TEXT,
            alici_adi TEXT,
            satis_tarihi TEXT,
            satis_fiyati REAL,
            FOREIGN KEY(kupeno) REFERENCES hayvanlar(kupeno)
        )''')

        for row in range(self.animal_table.rowCount()):
            kupeno = self.animal_table.item(row, 0).text()
            satis_fiyati = float(self.animal_table.item(row, 1).text())

            cursor_sales.execute('''
            INSERT INTO satis (kupeno, alici_adi, satis_tarihi, satis_fiyati)
            VALUES (?, ?, ?, ?)
            ''', (kupeno, alici_ad, satis_tarihi, satis_fiyati))

        conn_sales.commit()
        conn_sales.close()

        # E-Fatura PDF oluştur
        self.save_invoice(alici_ad, satis_tarihi)

        # Kullanıcıya başarı mesajı göster
        QMessageBox.information(self, "Başarılı", f"Hayvanlar satıldı. Alıcı: {alici_ad}, Tarih: {satis_tarihi}")
        self.alici_ad.clear()
        self.animal_table.setRowCount(0)

    def save_invoice(self, alici_ad, satis_tarihi):
        # Dosya kaydetme dialogu aç
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "E-Fatura Kaydet", "", "PDF Files (*.pdf);;All Files (*)", options=options)
        if file_path:
            self.generate_invoice(file_path, alici_ad, satis_tarihi)

    def generate_invoice(self, file_path, alici_ad, satis_tarihi):
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []

        # Stil ve tablo ayarları
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center alignment

        elements.append(Paragraph("E-Fatura", title_style))

        firma_logo = r'resimler\12122.png'
        maliye_logo = r'resimler\vergi.png'

        elements.append(Paragraph("<img src='%s' width='100' height='50'/> <img src='%s' width='100' height='50'/>" % (firma_logo, maliye_logo), styles['Normal']))

        elements.append(Paragraph("Vergi Dairesi: Hasan Tahsin Vergi Dairesi", styles['Normal']))
        elements.append(Paragraph("Vergi Numarasi: 132U9434734", styles['Normal']))

        elements.append(Paragraph(f"Alıcı Adı: {alici_ad}", styles['Normal']))
        elements.append(Paragraph(f"Satış Tarihi: {satis_tarihi}", styles['Normal']))

        # Satılan hayvanlar tablosu
        data = [['Küpe No', 'Satış Fiyatı (TL)']]
        for row in range(self.animal_table.rowCount()):
            kupeno = self.animal_table.item(row, 0).text()
            satis_fiyati = self.animal_table.item(row, 1).text()
            data.append([kupeno, satis_fiyati])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Toplam fiyat ve indirim
        total_price = sum(float(self.animal_table.item(row, 1).text()) for row in range(self.animal_table.rowCount()))
        elements.append(Paragraph(f"Toplam Fiyat: {total_price} TL", styles['Normal']))
        elements.append(Paragraph("İskonto: 0 TL", styles['Normal']))  # İskonto sabit olarak 0 TL

        doc.build(elements)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AnimalSalesApp()
    window.show()
    sys.exit(app.exec_())