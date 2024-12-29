import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QWidget, QMessageBox, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ModernUrunAlmaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürün Alma - Modern Arayüz")
        self.setGeometry(200, 200, 500, 400)
        self.setStyleSheet(self.get_stylesheet())

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Başlık
        self.title_label = QLabel("Ürün Alma Formu")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.layout.addWidget(self.title_label)

        # Form Alanları
        self.form_frame = QFrame()
        self.form_layout = QVBoxLayout(self.form_frame)

        self.urun_adi_label = QLabel("Ürün Adı:")
        self.urun_adi_input = QLineEdit()
        self.add_form_row(self.urun_adi_label, self.urun_adi_input)

        self.urun_fiyati_label = QLabel("Ürün Fiyatı:")
        self.urun_fiyati_input = QLineEdit()
        self.add_form_row(self.urun_fiyati_label, self.urun_fiyati_input)

        self.alim_tarihi_label = QLabel("Alım Tarihi (YYYY-MM-DD):")
        self.alim_tarihi_input = QLineEdit()
        self.add_form_row(self.alim_tarihi_label, self.alim_tarihi_input)

        self.tedarikci_adi_label = QLabel("Tedarikçi Adı:")
        self.tedarikci_adi_input = QLineEdit()
        self.add_form_row(self.tedarikci_adi_label, self.tedarikci_adi_input)

        self.layout.addWidget(self.form_frame)

        # Kaydet Butonu
        self.kaydet_buton = QPushButton("Kaydet")
        self.kaydet_buton.setCursor(Qt.PointingHandCursor)
        self.kaydet_buton.clicked.connect(self.veri_kaydet)
        self.layout.addWidget(self.kaydet_buton)

        # Ana widget'i ayarla
        self.setCentralWidget(self.central_widget)

    def add_form_row(self, label, input_field):
        """Form elemanlarını düzenli bir şekilde ekler."""
        row = QHBoxLayout()
        label.setFont(QFont("Arial", 12))
        input_field.setFont(QFont("Arial", 12))
        input_field.setFixedHeight(30)
        row.addWidget(label)
        row.addWidget(input_field)
        self.form_layout.addLayout(row)

    def veri_kaydet(self):
        # Kullanıcı girişlerini al
        urun_adi = self.urun_adi_input.text()
        urun_fiyati = self.urun_fiyati_input.text()
        alim_tarihi = self.alim_tarihi_input.text()
        tedarikci_adi = self.tedarikci_adi_input.text()

        # Girişlerin doğruluğunu kontrol et
        if not urun_adi or not urun_fiyati or not alim_tarihi or not tedarikci_adi:
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
            return

        try:
            urun_fiyati = float(urun_fiyati)  # Fiyatı kontrol et
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Ürün fiyatı sayı olmalıdır!")
            return

        # Veritabanına bağlan ve veriyi ekle
        try:
            baglanti = sqlite3.connect("veritabanları\alimlar.db")
            cursor = baglanti.cursor()

            ekle_sorgu = """
            INSERT INTO alimlar (urun_adi, urun_fiyati, alim_tarihi, tedarikci_adi)
            VALUES (?, ?, ?, ?)
            """
            cursor.execute(ekle_sorgu, (urun_adi, urun_fiyati, alim_tarihi, tedarikci_adi))
            baglanti.commit()
            baglanti.close()

            QMessageBox.information(self, "Başarılı", "Ürün başarıyla kaydedildi!")
            self.temizle()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")

    def temizle(self):
        """Form alanlarını temizler."""
        self.urun_adi_input.clear()
        self.urun_fiyati_input.clear()
        self.alim_tarihi_input.clear()
        self.tedarikci_adi_input.clear()

    @staticmethod
    def get_stylesheet():
        """Modern görünüm için stil sayfası."""
        return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLabel {
            color: #333333;
        }
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = ModernUrunAlmaApp()
    pencere.show()
    sys.exit(app.exec_())
