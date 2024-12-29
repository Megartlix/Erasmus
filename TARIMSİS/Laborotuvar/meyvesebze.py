import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QDoubleSpinBox, QPushButton, QLabel, QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QDate

class MeyveSebzeLaboratuvarFormu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meyve Sebze Laboratuvarı Veri Girişi")
        self.setGeometry(100, 100, 600, 600)

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
            QLineEdit, QDateEdit, QDoubleSpinBox, QComboBox {
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
        self.urun_adi_input = QLineEdit(self)
        self.urun_turu_input = QComboBox(self)
        self.urun_turu_input.addItems(["Meyve", "Sebze"])
        self.kilo_input = QDoubleSpinBox(self)
        self.kilo_input.setPrefix("Kg Cinsinden Kilo: ")
        self.kilo_input.setRange(0, 1000)
        self.asidik_deger_input = QDoubleSpinBox(self)
        self.asidik_deger_input.setRange(0, 14)
        self.seker_orani_input = QDoubleSpinBox(self)
        self.seker_orani_input.setSuffix(" %")
        self.seker_orani_input.setRange(0, 100)
        self.nem_orani_input = QDoubleSpinBox(self)
        self.nem_orani_input.setSuffix(" %")
        self.nem_orani_input.setRange(0, 100)
        self.ph_degeri_input = QDoubleSpinBox(self)
        self.ph_degeri_input.setRange(0, 14)
        self.mineraller_input = QLineEdit(self)
        self.pestisit_orani_input = QDoubleSpinBox(self)
        self.pestisit_orani_input.setRange(0, 100)

        # Ekle butonu
        self.ekle_button = QPushButton("Veriyi Ekle", self)
        self.ekle_button.clicked.connect(self.veri_ekle)

        # Geçmiş verileri gösterme butonu
        self.goruntule_button = QPushButton("Geçmiş Verileri Göster", self)
        self.goruntule_button.clicked.connect(self.veri_goruntule)

        # Tabloyu oluştur
        self.table_widget = QTableWidget(self)

        # Form elemanlarını düzenleme
        self.form_layout.addRow("Tarih:", self.tarih_input)
        self.form_layout.addRow("Ürün Adı:", self.urun_adi_input)
        self.form_layout.addRow("Ürün Türü:", self.urun_turu_input)
        self.form_layout.addRow("Kilo (kg):", self.kilo_input)
        self.form_layout.addRow("Asidik Değer:", self.asidik_deger_input)
        self.form_layout.addRow("Şeker Oranı (%):", self.seker_orani_input)
        self.form_layout.addRow("Nem Oranı (%):", self.nem_orani_input)
        self.form_layout.addRow("pH Değeri:", self.ph_degeri_input)
        self.form_layout.addRow("Mineraller:", self.mineraller_input)
        self.form_layout.addRow("Pestisit Oranı (%):", self.pestisit_orani_input)

        # Layout'a butonları ve tabloyu ekle
        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.ekle_button)
        self.layout.addWidget(self.goruntule_button)
        self.layout.addWidget(self.table_widget)

        self.setLayout(self.layout)

    def veri_ekle(self):
        # Veritabanı bağlantısı
        conn = sqlite3.connect("veritabanları/meyve_sebze_laboratuvar.db")
        cursor = conn.cursor()

        # Verileri al
        tarih = self.tarih_input.text()
        urun_adi = self.urun_adi_input.text()
        urun_turu = self.urun_turu_input.currentText()
        kilo = self.kilo_input.value()
        asidik_deger = self.asidik_deger_input.value()
        seker_orani = self.seker_orani_input.value()
        nem_orani = self.nem_orani_input.value()
        ph_degeri = self.ph_degeri_input.value()
        mineraller = self.mineraller_input.text()
        pestisit_orani = self.pestisit_orani_input.value()

        # Veriyi veritabanına ekle
        cursor.execute("""
        INSERT INTO analizler (tarih, urun_adi, urun_turu, kilo, asidik_deger, seker_orani, nem_orani, ph_degeri, mineraller, pestisit_orani)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tarih, urun_adi, urun_turu, kilo, asidik_deger, seker_orani, nem_orani, ph_degeri, mineraller, pestisit_orani))

        # Değişiklikleri kaydet ve bağlantıyı kapat
        conn.commit()
        conn.close()

        # Başarı mesajı
        print("Veri başarıyla eklendi!")

    def veri_goruntule(self):
        # Veritabanı bağlantısı
        conn = sqlite3.connect("veritabanları/meyve_sebze_laboratuvar.db")
        cursor = conn.cursor()

        # Veritabanındaki tüm verileri al
        cursor.execute("SELECT * FROM analizler")
        veriler = cursor.fetchall()

        # Tabloyu temizle
        self.table_widget.setRowCount(0)

        # Tabloyu doldur
        for row_number, row_data in enumerate(veriler):
            self.table_widget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table_widget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        # Tabloyu ayarla (kolon sayısı)
        self.table_widget.setColumnCount(len(veriler[0]) if veriler else 0)

        # Veritabanı bağlantısını kapat
        conn.close()

# PyQt5 uygulamasını başlat
app = QApplication(sys.argv)
window = MeyveSebzeLaboratuvarFormu()
window.show()
sys.exit(app.exec_())
