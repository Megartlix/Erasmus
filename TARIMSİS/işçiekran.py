import sys
import sqlite3
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                             QVBoxLayout, QWidget, QHBoxLayout, QMessageBox, 
                             QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

DB_NAME = r'veritabanları\kullanicilar.db'

def get_user_name(username):
    conn = sqlite3.connect("veritabanları\kullanicilar.db")
    cursor = conn.cursor()
    cursor.execute("SELECT kullanici_adi FROM kullanicilar WHERE kullanici_adi=?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return "yönetici "

class AdminPanel(QMainWindow):
    def __init__(self, kullanici_adi):
        super().__init__()
        self.kullanici_adi = get_user_name(kullanici_adi)
        self.setWindowTitle('İşçi')
        self.setGeometry(300, 150, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #263238;
                color: #FFFFFF;
                font-family: 'Roboto', sans-serif;
            }
        """)

        main_layout = QVBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("gronova.png")
        logo_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignLeft)

        self.user_label = QLabel(f'Hoşgeldiniz, {self.kullanici_adi}')
        self.user_label.setFont(QFont('Roboto', 14, QFont.Bold))
        self.user_label.setStyleSheet("color: #FFEB3B;")

        top_layout = QHBoxLayout()
        top_layout.addWidget(logo_label)
        top_layout.addWidget(self.user_label)
        main_layout.addLayout(top_layout)

        grid_layout = QGridLayout()
        self.create_cards(grid_layout)
        main_layout.addLayout(grid_layout)

        exit_button = QPushButton("Çıkış")
        exit_button.setIcon(QIcon('exit_icon.png'))
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: #FFFFFF;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)
        exit_button.clicked.connect(self.close)
        main_layout.addWidget(exit_button, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.statusBar().showMessage("Hazır")
        self.statusBar().setStyleSheet("background-color: #37474F; color: #FFFFFF;")

    def create_cards(self, layout):
        card_info = [
            ("Görev Kontrol", "işçi.py"),
        
             
   
        ]

        for index, (title, file_name) in enumerate(card_info):
            card = self.create_card(title, file_name)
            row = index // 3  
            col = index % 3
            layout.addWidget(card, row, col)

    def create_card(self, title, file_name):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #37474F;
                border-radius: 12px;
                padding: 20px;
                color: #FFFFFF;
                transition: background-color 0.3s;
            }
            QFrame:hover {
                background-color: #455A64;
            }
        """)
        card_layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setFont(QFont('Roboto', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)

        btn_open = QPushButton('Aç')
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4;
                color: #FFFFFF;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-size: 14px;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #0097A7;
            }
        """)
        btn_open.clicked.connect(lambda: self.open_file(file_name))

        card_layout.addWidget(title_label)
        card_layout.addWidget(btn_open)
        return card

    def open_file(self, file_name):
        try:
            subprocess.Popen(['python', file_name])
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Dosyayı açarken bir hata oluştu: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(38, 50, 56))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    window = AdminPanel("")
    window.show()
    sys.exit(app.exec_())