import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class SutAnalizleriApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initDB()

    def initUI(self):
        self.setWindowTitle('Süt Analizleri')
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout()

        # Başlık
        title = QLabel("Süt Analiz Tarımsis")
        title.setFont(QFont('Arial', 20))
        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)

        form_layout = QFormLayout()

        # Giriş alanları
        self.tarih_input = self.create_input()
        self.sahip_adi_input = self.create_input()
        self.kupe_no_input = self.create_input()
        self.sut_miktari_input = self.create_input()
        self.yag_orani_input = self.create_input()
        self.protein_orani_input = self.create_input()
        self.ph_degeri_input = self.create_input()
        self.laktoz_orani_input = self.create_input()
        self.bakteri_sayisi_input = self.create_input()
        self.urea_degeri_input = self.create_input()

        form_layout.addRow('Tarih:', self.tarih_input)
       
        form_layout.addRow('Küpe No:', self.kupe_no_input)
        form_layout.addRow('Süt Miktarı:', self.sut_miktari_input)
        form_layout.addRow('Yağ Oranı:', self.yag_orani_input)
        form_layout.addRow('Protein Oranı:', self.protein_orani_input)
        form_layout.addRow('pH Değeri:', self.ph_degeri_input)
        form_layout.addRow('Laktoz Oranı:', self.laktoz_orani_input)
        form_layout.addRow('Bakteri Sayısı:', self.bakteri_sayisi_input)
        form_layout.addRow('Üre Değeri:', self.urea_degeri_input)

        self.add_button = QPushButton('Veriyi Ekle')
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.add_data)

        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def create_input(self):
        input_field = QLineEdit()
        input_field.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        return input_field

    def initDB(self):
        self.conn = sqlite3.connect('veritabanları\sut_laboratuvar.db')
        self.cursor = self.conn.cursor()

        
        self.conn.commit()

    def add_data(self):
        tarih = self.tarih_input.text()
        sahip_adi = self.sahip_adi_input.text()
        kupe_no = self.kupe_no_input.text()
        sut_miktari = float(self.sut_miktari_input.text())
        yag_orani = float(self.yag_orani_input.text())
        protein_orani = float(self.protein_orani_input.text())
        ph_degeri = float(self.ph_degeri_input.text())
        laktoz_orani = float(self.laktoz_orani_input.text())
        bakteri_sayisi = int(self.bakteri_sayisi_input.text())
        urea_degeri = float(self.urea_degeri_input.text())

        self.cursor.execute('''INSERT INTO sut_analizleri (tarih, sahip_adi, kupe_no, sut_miktari, yag_orani, protein_orani, ph_degeri, laktoz_orani, bakteri_sayisi, urea_degeri) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (tarih, sahip_adi, kupe_no, sut_miktari, yag_orani, protein_orani, ph_degeri, laktoz_orani, bakteri_sayisi, urea_degeri))
        self.conn.commit()

        QMessageBox.information(self, 'Başarılı', 'Veri başarıyla eklendi!')
        self.clear_inputs()

    def clear_inputs(self):
        self.tarih_input.clear()
        self.sahip_adi_input.clear()
        self.kupe_no_input.clear()
        self.sut_miktari_input.clear()
        self.yag_orani_input.clear()
        self.protein_orani_input.clear()
        self.ph_degeri_input.clear()
        self.laktoz_orani_input.clear()
        self.bakteri_sayisi_input.clear()
        self.urea_degeri_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SutAnalizleriApp()
    ex.show()
    sys.exit(app.exec_())