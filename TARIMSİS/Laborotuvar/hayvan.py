import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox, QPushButton, QLabel, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QDate

class HayvanlarLaboratuvarFormu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hayvanlar İçin Laboratuvar Veri Girişi")
        self.setGeometry(100, 100, 400, 600)  # Boyutu biraz daha genişlettik

        # Modern bir tema ile arka plan rengi ve font stili
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f9;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QDateEdit, QDoubleSpinBox, QTextEdit, QComboBox {
                padding: 8px;
                border-radius: 5px;
                background-color: #e9ecef;
                border: 1px solid #ccc;
            }
            QTableWidget {
                margin-top: 20px;
                background-color: #fff;
                border: 1px solid #ccc;
            }
        """)

        # Ana düzen
        self.layout = QVBoxLayout()

        # Form düzeni
        self.form_layout = QFormLayout()

        # Form elemanları
        self.tarih_input = QDateEdit(self)
        self.tarih_input.setDate(QDate.currentDate())
        self.hayvan_adi_input = QLineEdit(self)
        self.hayvan_turu_input = QComboBox(self)
        self.hayvan_turu_input.addItems(["İnek", "Koyun", "Keçi", "Diğer"])
        self.kilolama_input = QDoubleSpinBox(self)
        self.kilolama_input.setPrefix("Kg: ")
        self.kilolama_input.setRange(0, 1000)
        self.kan_sonucu_input = QTextEdit(self)
        self.tahlil_sonucu_input = QTextEdit(self)
        self.veteriner_raporu_input = QTextEdit(self)
        self.genetik_test_input = QTextEdit(self)
        self.hastalik_tespiti_input = QTextEdit(self)
        self.tedavi_durum_input = QTextEdit(self)

        # Ekle butonu
        self.ekle_button = QPushButton("Veriyi Ekle", self)
        self.ekle_button.clicked.connect(self.veri_ekle)

        # Geçmiş sonuçları gösteren alan
        self.gecmis_sonuclar_label = QLabel("Geçmiş Sonuçlar:", self)
        self.gecmis_sonuclar_edit = QTextEdit(self)
        self.gecmis_sonuclar_edit.setReadOnly(True)

        # Form elemanlarını düzenleme
        self.form_layout.addRow("Tarih:", self.tarih_input)
        self.form_layout.addRow("Hayvan Adı:", self.hayvan_adi_input)
        self.form_layout.addRow("Hayvan Türü:", self.hayvan_turu_input)
        self.form_layout.addRow("Kilolama (kg):", self.kilolama_input)
        self.form_layout.addRow("Kan Sonucu:", self.kan_sonucu_input)
        self.form_layout.addRow("Tahlil Sonucu:", self.tahlil_sonucu_input)
        self.form_layout.addRow("Veteriner Raporu:", self.veteriner_raporu_input)
        self.form_layout.addRow("Genetik Test Sonucu:", self.genetik_test_input)
        self.form_layout.addRow("Hastalık Tespiti:", self.hastalik_tespiti_input)
        self.form_layout.addRow("Tedavi Durumu:", self.tedavi_durum_input)

        # Ekleme butonunu ekle
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.ekle_button)
        self.layout.addWidget(self.gecmis_sonuclar_label)
        self.layout.addWidget(self.gecmis_sonuclar_edit)

        self.setLayout(self.layout)

        # Geçmiş verileri yükle
        self.gecmis_verileri_yukle()

    def veri_ekle(self):
        # Veritabanı bağlantısı
        conn = sqlite3.connect("veritabanları/hayvanlar_laboratuvar.db")
        cursor = conn.cursor()

        # Verileri al
        tarih = self.tarih_input.text()
        hayvan_adi = self.hayvan_adi_input.text()
        hayvan_turu = self.hayvan_turu_input.currentText()
        kilolama = self.kilolama_input.value()
        kan_sonucu = self.kan_sonucu_input.toPlainText()
        tahlil_sonucu = self.tahlil_sonucu_input.toPlainText()
        veteriner_raporu = self.veteriner_raporu_input.toPlainText()
        genetik_test = self.genetik_test_input.toPlainText()
        hastalik_tespiti = self.hastalik_tespiti_input.toPlainText()
        tedavi_durum = self.tedavi_durum_input.toPlainText()

        # Veriyi veritabanına ekle
        cursor.execute("""
        INSERT INTO analizler (tarih, hayvan_adi, hayvan_turu, kilolama, kan_sonucu, tahlil_sonucu, veteriner_raporu, genetik_test, hastalik_tespiti, tedavi_durum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tarih, hayvan_adi, hayvan_turu, kilolama, kan_sonucu, tahlil_sonucu, veteriner_raporu, genetik_test, hastalik_tespiti, tedavi_durum))

        # Değişiklikleri kaydet ve bağlantıyı kapat
        conn.commit()
        conn.close()

        # Geçmiş verileri yükle
        self.gecmis_verileri_yukle()

        # Başarı mesajı
        print("Veri başarıyla eklendi!")

    def gecmis_verileri_yukle(self):
        # Veritabanı bağlantısı
        conn = sqlite3.connect("veritabanları/hayvanlar_laboratuvar.db")
        cursor = conn.cursor()

        # Geçmiş verileri sorgula
        cursor.execute("SELECT * FROM analizler ORDER BY tarih DESC")
        rows = cursor.fetchall()

        # Geçmiş sonuçları QTextEdit alanına yaz
        self.gecmis_sonuclar_edit.clear()
        for row in rows:
            self.gecmis_sonuclar_edit.append(f"Tarih: {row[1]}, Hayvan: {row[2]}, Tür: {row[3]}, Kilolama: {row[4]}kg\nKan Sonucu: {row[5]}\n")

        conn.close()

# PyQt5 uygulamasını başlat
app = QApplication(sys.argv)
window = HayvanlarLaboratuvarFormu()
window.show()
sys.exit(app.exec_())
