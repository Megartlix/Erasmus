import sys
import sqlite3
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, 
                             QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

# Veritabanı dosyasının ismi
DB_NAME = r'C:\Users\Süleyman AKBULUT\Music\TARIMSİS\veritabanları\kullanicilar.db'

# Kullanıcı adı veritabanından çekme fonksiyonu
def get_user_name(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT kullanici_adi FROM kullanicilar WHERE kullanici_adi=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "Bilinmeyen Kullanıcı"

# Yönetici paneli için ana pencere sınıfı
class AdminPanel(QMainWindow):
    def __init__(self, kullanici_adi):
        super().__init__()
        self.kullanici_adi = kullanici_adi

        # Veritabanından kullanıcı adını çek
        self.kullanici_adi = get_user_name(self.kullanici_adi)

        self.setWindowTitle('Yönetim Paneli')
        self.setGeometry(300, 150, 1200, 800)
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")

        # Ana layout
        main_layout = QVBoxLayout()
        
        # Üst kısımda kullanıcı adını göster
        self.user_label = QLabel(f'Hoşgeldiniz, {self.kullanici_adi}')
        self.user_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.user_label.setAlignment(Qt.AlignCenter)
        self.user_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.user_label)

        # Kartların yer alacağı grid layout
        grid_layout = QGridLayout()

        # Kartları ekle
        self.create_cards(grid_layout)

        # Ana layouta grid layout'u ekle
        main_layout.addLayout(grid_layout)

        # Merkezi widget olarak ayarlama
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    # Kart oluşturma fonksiyonu
    def create_cards(self, layout):
        # Kart isimleri ve yönlendirecekleri dosyalar
        card_info = [
            ("Görev Merkezi", "işçi.py"),
            ("Yemek Durumu", "dosya2.py"),
            
            
        ]

        # Kartları oluştur ve grid layout'a ekle
        for index, (title, file_name) in enumerate(card_info):
            card = self.create_card(title, file_name)
            row = index // 3  # Her satırda 3 kart olacak
            col = index % 3
            layout.addWidget(card, row, col)

    # Tek bir kart oluşturma fonksiyonu
    def create_card(self, title, file_name):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #444444;
                border-radius: 10px;
                padding: 20px;
                color: #FFFFFF;
            }
            QFrame:hover {
                background-color: #555555;
            }
        """)
        card_layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        btn_open = QPushButton('Aç')
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #00CED1;
                color: #FFFFFF;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #008B8B;
            }
        """)
        btn_open.clicked.connect(lambda: self.open_file(file_name))

        card_layout.addWidget(title_label)
        card_layout.addWidget(btn_open)
        return card

    # Dosyayı açma fonksiyonu
    def open_file(self, file_name):
        try:
            subprocess.Popen(['python', file_name])
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Dosyayı açarken bir hata oluştu: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Tema renkleri
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    # Giriş yapan kullanıcının adı, örneğin "yonetici1"
    window = AdminPanel("result")
    window.show()
    sys.exit(app.exec_())
