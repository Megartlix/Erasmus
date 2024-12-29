import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import barcode
from barcode.writer import ImageWriter
from PIL import Image

class BarcodeApp(QWidget):
    def __init__(self):
        super().__init__()

        # Arayüz bileşenlerini oluştur
        self.init_ui()

    def init_ui(self):
        # Uygulama başlığı
        self.setWindowTitle('BEDROCK TARIMSİSBARKOD ÜRETİCİ')

        # Ana layout
        layout = QVBoxLayout()

        # Üst yazı (TARIMZİO)
        self.title_label = QLabel('BEDROCK TEAM TARIMSİS', self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont('Orbitron', 36, QFont.Bold))  # Modern ve futuristik bir font
        self.title_label.setStyleSheet('color: #00ff99;')  # Yeşil renk
        layout.addWidget(self.title_label)

        # Ürün ismi girişi
        self.product_name_input = QLineEdit(self)
        self.product_name_input.setPlaceholderText('Ürün ismini girin')
        layout.addWidget(self.product_name_input)

        # Barkod görüntüsü
        self.barcode_label = QLabel(self)
        layout.addWidget(self.barcode_label)

        # Barkod oluştur butonu
        self.generate_button = QPushButton('Barkod Oluştur', self)
        self.generate_button.clicked.connect(self.generate_barcode)
        layout.addWidget(self.generate_button)

        # Kaydet butonu
        self.save_button = QPushButton('Barkodu Kaydet', self)
        self.save_button.clicked.connect(self.save_barcode)
        layout.addWidget(self.save_button)

        # Yazdır butonu
        self.print_button = QPushButton('Barkodu Yazdır', self)
        self.print_button.clicked.connect(self.print_barcode)
        layout.addWidget(self.print_button)

        # Layout'u pencereye ekle
        self.setLayout(layout)

        # Tema uygulaması
        self.apply_theme()

    def apply_theme(self):
        # 2050 Teması için stil uygulaması
        self.setStyleSheet("""
            QWidget {
                background-color: #212121;
                color: #fff;
                font-family: 'Arial', sans-serif;
            }

            QLineEdit {
                background-color: #333;
                border: 2px solid #555;
                padding: 10px;
                color: #fff;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #00ff99;
            }

            QPushButton {
                background-color: #00ff99;
                border: none;
                color: white;
                padding: 12px;
                font-size: 16px;
                border-radius: 8px;
                transition: background-color 0.3s ease;
            }

            QPushButton:hover {
                background-color: #33cc66;
            }

            QLabel {
                font-size: 18px;
                margin-top: 20px;
                color: #fff;
            }
        """)

    def generate_barcode(self):
        # Ürün ismini al
        product_name = self.product_name_input.text()

        if not product_name:
            return

        # Barkod oluştur
        barcode_data = barcode.get('ean13', product_name.zfill(12), writer=ImageWriter())
        barcode_image = barcode_data.render()

        # Barkod görseline logo ekleyelim
        self.add_logo_to_barcode(barcode_image)

        # Barkod görüntüsünü QLabel üzerinde göster
        barcode_image.save('barcode_with_logo.png')  # Geçici kaydetme
        pixmap = QPixmap('barcode_with_logo.png')
        self.barcode_label.setPixmap(pixmap)
        self.barcode_label.setAlignment(Qt.AlignCenter)

    def add_logo_to_barcode(self, barcode_image):
        # Logoyu ekleyelim
        try:
            # Logoyu aç
            logo = Image.open(r'C:\Users\Süleyman AKBULUT\Music\TARIMSİS\resimler\Bedrock Team logo with a modern and beautiful design.png')

            # Logo boyutunu barkod boyutuna göre ayarlayalım
            logo_size = (barcode_image.width // 5, barcode_image.height // 5)  # Logoyu küçültüyoruz
            logo = logo.resize(logo_size, Image.Resampling.LANCZOS)  # Logo boyutlandırma

            # Barkod görselinin üzerine logoyu yerleştirelim
            barcode_image.paste(logo, (barcode_image.width // 2 - logo.width // 2, barcode_image.height // 2 - logo.height // 2), logo.convert("RGBA"))
        except Exception as e:
            print("Logo ekleme sırasında bir hata oluştu:", e)

    def save_barcode(self):
        # Kullanıcıya dosya kaydetme penceresi açma
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix('png')
        file_path, _ = file_dialog.getSaveFileName(self, 'Barkodu Kaydet', '', 'PNG Files (*.png);;All Files (*)')

        if file_path:
            # Seçilen yolda barkodu kaydedelim
            barcode_image = Image.open('barcode_with_logo.png')
            barcode_image.save(file_path)
            print(f"Barkod kaydedildi: {file_path}")

    def print_barcode(self):
        # Yazdırma işlemi için QPrinter kullanacağız
        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)

        # Yazdırma penceresi açılır
        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            painter = QPrinter(printer)
            pixmap = QPixmap('barcode_with_logo.png')  # Yeni kaydedilen barkod ile yazdırma
            painter.drawPixmap(100, 100, pixmap)  # Barkodu yazdır
            painter.end()


def main():
    app = QApplication(sys.argv)
    ex = BarcodeApp()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
