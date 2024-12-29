import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox, QPushButton, QLabel
from PyQt5.QtCore import QDate

class EtLaboratuvarFormu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Et Laboratuvarı Veri Girişi")
        self.setGeometry(100, 100, 400, 400)

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
            QLineEdit, QDateEdit, QDoubleSpinBox {
                padding: 8px;
                border-radius: 5px;
                background-color: #e9ecef;
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
        self.kupe_no_input = QLineEdit(self)
        self.et_miktari_input = QDoubleSpinBox(self)
        self.et_miktari_input.setPrefix("Kg Cinsinden Et Miktarı: ")
        self.et_miktari_input.setRange(0, 1000)
        self.protein_orani_input = QDoubleSpinBox(self)
        self.protein_orani_input.setSuffix(" %")
        self.protein_orani_input.setRange(0, 100)
        self.yag_orani_input = QDoubleSpinBox(self)
        self.yag_orani_input.setSuffix(" %")
        self.yag_orani_input.setRange(0, 100)
        self.nem_orani_input = QDoubleSpinBox(self)
        self.nem_orani_input.setSuffix(" %")
        self.nem_orani_input.setRange(0, 100)
        self.ph_degeri_input = QDoubleSpinBox(self)
        self.ph_degeri_input.setRange(0, 14)
        self.sertlik_input = QDoubleSpinBox(self)
        self.sertlik_input.setRange(0, 10)
        self.bakteri_sayisi_input = QDoubleSpinBox(self)
        self.bakteri_sayisi_input.setRange(0, 10000)

        # Kombinasyon kutusu
        self.kupe_no_input.setPlaceholderText("Küpe Numarası Girin")

        # Ekle butonu
        self.ekle_button = QPushButton("Veriyi Ekle", self)
        self.ekle_button.clicked.connect(self.veri_ekle)

        # Form elemanlarını düzenleme
        self.form_layout.addRow("Tarih:", self.tarih_input)
        self.form_layout.addRow("Küpe No:", self.kupe_no_input)
        self.form_layout.addRow("Et Miktarı (kg):", self.et_miktari_input)
        self.form_layout.addRow("Protein Oranı (%):", self.protein_orani_input)
        self.form_layout.addRow("Yağ Oranı (%):", self.yag_orani_input)
        self.form_layout.addRow("Nem Oranı (%):", self.nem_orani_input)
        self.form_layout.addRow("pH Değeri:", self.ph_degeri_input)
        self.form_layout.addRow("Sertlik:", self.sertlik_input)
        self.form_layout.addRow("Bakteri Sayısı:", self.bakteri_sayisi_input)

        # Ekleme butonunu ekle
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.ekle_button)

        self.setLayout(self.layout)

    def veri_ekle(self):
        # Veritabanı bağlantısı
        conn = sqlite3.connect(r"veritabanları\et_laboratuvar.db")
        cursor = conn.cursor()

        # Verileri al
        tarih = self.tarih_input.text()
        kupe_no = self.kupe_no_input.text()
        et_miktari = self.et_miktari_input.value()
        protein_orani = self.protein_orani_input.value()
        yag_orani = self.yag_orani_input.value()
        nem_orani = self.nem_orani_input.value()
        ph_degeri = self.ph_degeri_input.value()
        sertlik = self.sertlik_input.value()
        bakteri_sayisi = self.bakteri_sayisi_input.value()

        # Veriyi veritabanına ekle
        cursor.execute("""
        INSERT INTO et_analizleri (tarih, kupe_no, et_miktari, protein_orani, yag_orani, nem_orani, ph_degeri, sertlik, bakteri_sayisi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tarih, kupe_no, et_miktari, protein_orani, yag_orani, nem_orani, ph_degeri, sertlik, bakteri_sayisi))

        # Değişiklikleri kaydet ve bağlantıyı kapat
        conn.commit()
        conn.close()

        # Başarı mesajı
        print("Veri başarıyla eklendi!")

# PyQt5 uygulamasını başlat
app = QApplication(sys.argv)
window = EtLaboratuvarFormu()
window.show()
sys.exit(app.exec_())
