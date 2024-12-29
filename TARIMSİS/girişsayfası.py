import sys
import sqlite3
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPixmap


DB_NAME = r'C:\Users\Süleyman AKBULUT\Music\TARIMSİS\veritabanları\kullanicilar.db'


def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Initialize the database schema if necessary
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT NOT NULL,
        sifre TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Giriş Sayfası')
        self.setGeometry(500, 200, 400, 300)
        self.setWindowIcon(QIcon('icon.png'))  # Use a custom icon

        # Set application style
        self.setStyleSheet("background-color: #1E1E1E; color: #FFFFFF; font-family: Arial;")

        # Labels
        self.label_kullanici = QLabel('Kullanıcı Adı:', self)
        self.label_sifre = QLabel('Şifre:', self)
        self.label_rol = QLabel('Rol:', self)

        # Inputs
        self.input_kullanici = QLineEdit(self)
        self.input_sifre = QLineEdit(self)
        self.input_sifre.setEchoMode(QLineEdit.Password)

        # ComboBox
        self.combo_rol = QComboBox(self)
        self.combo_rol.addItems(['Yönetici', 'Formen', 'İşçi'])

        # Button
        self.btn_giris = QPushButton('Giriş Yap', self)
        self.btn_giris.clicked.connect(self.giris_yap)

        # Apply styles
        self.apply_styles()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_kullanici)
        layout.addWidget(self.input_kullanici)
        layout.addWidget(self.label_sifre)
        layout.addWidget(self.input_sifre)
        layout.addWidget(self.label_rol)
        layout.addWidget(self.combo_rol)
        layout.addWidget(self.btn_giris)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def giris_yap(self):
        kullanici_adi = self.input_kullanici.text()
        sifre = self.input_sifre.text()
        rol = self.combo_rol.currentText()

        if self.dogrula_kullanici(kullanici_adi, sifre, rol):
            QMessageBox.information(self, 'Başarılı', 'Giriş başarılı!')
            self.yonlendir(rol)
        else:
            QMessageBox.warning(self, 'Hata', 'Kullanıcı adı, şifre veya rol hatalı!')

    def dogrula_kullanici(self, kullanici_adi, sifre, rol):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=? AND rol=?
        ''', (kullanici_adi, sifre, rol))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def yonlendir(self, rol):
        if rol == 'Yönetici':
            subprocess.Popen(['python', r'Yöneticipaneli.py'])
        elif rol == 'Formen':
            subprocess.Popen(['python', 'formen.py'])
        elif rol == 'İşçi':
            subprocess.Popen(['python', 'isci.py'])

    def apply_styles(self):
        self.label_kullanici.setStyleSheet("font-size: 14px; padding: 5px;")
        self.label_sifre.setStyleSheet("font-size: 14px; padding: 5px;")
        self.label_rol.setStyleSheet("font-size: 14px; padding: 5px;")

        self.input_kullanici.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #008080;
                border-radius: 10px;
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
        """)
        self.input_sifre.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #008080;
                border-radius: 10px;
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
        """)

        self.combo_rol.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #008080;
                border-radius: 10px;
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
        """)

        self.btn_giris.setStyleSheet("""
            QPushButton {
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 10px;
                background-color: #008080;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #005959;
            }
        """)


if __name__ == '__main__':
    initialize_database()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())