import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QWidget, QFormLayout, 
                             QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

# Veritabanı dosyasının ismi
DB_NAME = r'veritabanları\kullanicilar.db'

# Veritabanına formen ekleme fonksiyonu
def add_formen_to_db(worker_id, username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kullanicilar (id, kullanici_adi, sifre, rol) VALUES (?, ?, ?, ?)", 
                   (worker_id, username, password, 'formen'))
    conn.commit()
    conn.close()

# Formen Ekleme Ekranı
class FormenAddScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Formen Ekle')
        self.setGeometry(300, 150, 400, 300)
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")

        # Ana layout
        main_layout = QVBoxLayout()

        # Başlık
        self.header_label = QLabel('Yeni Formen Ekle')
        self.header_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.header_label)

        # Form Layout
        form_layout = QFormLayout()

        # ID, Kullanıcı Adı ve Şifre için alanlar
        self.worker_id_input = QLineEdit()
        self.worker_id_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.worker_id_input.setPlaceholderText("Formen ID")

        self.username_input = QLineEdit()
        self.username_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.username_input.setPlaceholderText("Kullanıcı Adı")

        self.password_input = QLineEdit()
        self.password_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)  # Şifreyi gizli tutar

        form_layout.addRow('Formen ID:', self.worker_id_input)
        form_layout.addRow('Kullanıcı Adı:', self.username_input)
        form_layout.addRow('Şifre:', self.password_input)

        # Formen Ekle butonu
        self.add_button = QPushButton('Formen Ekle')
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #00CED1;
                color: #FFFFFF;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #008B8B;
            }
        """)
        self.add_button.clicked.connect(self.add_formen)

        # Form ve butonu layout'a ekleyelim
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.add_button)

        # Merkezi widget olarak ayarlama
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_formen(self):
        # Kullanıcıdan alınan veriler
        worker_id = self.worker_id_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # Gerekli alanların dolu olup olmadığını kontrol et
        if not worker_id or not username or not password:
            QMessageBox.warning(self, 'Hata', 'Lütfen tüm alanları doldurun!')
            return

        # Veritabanına formen'i ekle
        try:
            add_formen_to_db(worker_id, username, password)
            QMessageBox.information(self, 'Başarılı', 'Formen başarıyla eklendi!')
            self.clear_fields()
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Formen eklenirken bir hata oluştu: {e}')

    # Alanları temizleme fonksiyonu
    def clear_fields(self):
        self.worker_id_input.clear()
        self.username_input.clear()
        self.password_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Tema renkleri
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    # Formen Ekleme ekranını göster
    window = FormenAddScreen()
    window.show()
    sys.exit(app.exec_())
