
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class TarlaAnalizi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tarla Analiz Programı")
        self.setGeometry(100, 100, 800, 600)

        # Ana widget ve layout oluşturma
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Butonlar ve etiketler
        self.resim_sec_btn = QPushButton("Tarla Resmi Seç")
        self.resim_label = QLabel()
        self.isi_haritasi_label = QLabel()
        self.verim_haritasi_label = QLabel()

        # Layout'a widget'ları ekleme
        self.layout.addWidget(self.resim_sec_btn)
        self.layout.addWidget(self.resim_label)
        self.layout.addWidget(self.isi_haritasi_label)
        self.layout.addWidget(self.verim_haritasi_label)

        # Buton bağlantısı
        self.resim_sec_btn.clicked.connect(self.resim_sec)

    def resim_sec(self):
        dosya_yolu, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if dosya_yolu:
            # Resmi yükleme ve gösterme
            resim = cv2.imread(dosya_yolu)
            resim_rgb = cv2.cvtColor(resim, cv2.COLOR_BGR2RGB)
            
            # Orijinal resmi gösterme
            h, w, ch = resim_rgb.shape
            bytes_per_line = ch * w
            qt_resim = QImage(resim_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_resim)
            self.resim_label.setPixmap(pixmap.scaled(400, 300))

            # Isı haritası oluşturma
            gri_resim = cv2.cvtColor(resim, cv2.COLOR_BGR2GRAY)
            isi_haritasi = cv2.applyColorMap(gri_resim, cv2.COLORMAP_JET)
            isi_haritasi_rgb = cv2.cvtColor(isi_haritasi, cv2.COLOR_BGR2RGB)
            
            # Isı haritasını gösterme
            h, w, ch = isi_haritasi_rgb.shape
            bytes_per_line = ch * w
            qt_isi = QImage(isi_haritasi_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            isi_pixmap = QPixmap.fromImage(qt_isi)
            self.isi_haritasi_label.setPixmap(isi_pixmap.scaled(400, 300))

            # Verim haritası oluşturma (örnek olarak yeşillik oranına göre)
            hsv = cv2.cvtColor(resim, cv2.COLOR_BGR2HSV)
            yesil_alt = np.array([35, 50, 50])
            yesil_ust = np.array([85, 255, 255])
            maske = cv2.inRange(hsv, yesil_alt, yesil_ust)
            verim_haritasi = cv2.bitwise_and(resim, resim, mask=maske)
            verim_haritasi_rgb = cv2.cvtColor(verim_haritasi, cv2.COLOR_BGR2RGB)

            # Verim haritasını gösterme
            h, w, ch = verim_haritasi_rgb.shape
            bytes_per_line = ch * w
            qt_verim = QImage(verim_haritasi_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            verim_pixmap = QPixmap.fromImage(qt_verim)
            self.verim_haritasi_label.setPixmap(verim_pixmap.scaled(400, 300))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = TarlaAnalizi()
    pencere.show()
    sys.exit(app.exec_())
