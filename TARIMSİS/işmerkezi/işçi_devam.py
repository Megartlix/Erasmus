import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                             QComboBox, QMessageBox, QDateEdit, QLineEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPalette, QColor, QFont


DB_NAME_USERS = r'veritabanları\kullanicilar.db'  # Kullanıcılar veritabanı
DB_NAME_ATTENDANCE = r'veritabanları\devamagadevam.db'  # Devamsızlık veritabanı


def save_attendance(user_id, date, status):
    conn = sqlite3.connect(DB_NAME_ATTENDANCE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO devamsizliklar (kullanici_id, tarih, durum) 
        VALUES (?, ?, ?)
    """, (user_id, date, status))
    conn.commit()
    conn.close()


class WorkerForemanPanel(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('İşçi/Formen Paneli')
        self.setGeometry(300, 150, 500, 400)
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")

       
        main_layout = QVBoxLayout()

    
        self.header_label = QLabel('Devam Durumu Belirleme')
        self.header_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.header_label)

        # İşçi ID girişi
        self.worker_id_input = QLineEdit()
        self.worker_id_input.setPlaceholderText('İşçi ID Giriniz')
        self.worker_id_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        main_layout.addWidget(self.worker_id_input)

        # Tarih seçimi
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        main_layout.addWidget(self.date_edit)

        # Devam durumu seçimi
        self.status_combo = QComboBox()
        self.status_combo.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.status_combo.addItem("Geldi")
        self.status_combo.addItem("Gelmedi")
        self.status_combo.addItem("İzinli")
        main_layout.addWidget(self.status_combo)

        # Devam durumu kaydet butonu
        self.save_button = QPushButton('Devam Durumunu Kaydet')
        self.save_button.setStyleSheet("""
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
        self.save_button.clicked.connect(self.save_attendance)
        main_layout.addWidget(self.save_button)

        # Merkezi widget ayarlama
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def save_attendance(self):
        user_id = self.worker_id_input.text()
        date = self.date_edit.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        if not user_id:
            QMessageBox.warning(self, 'Hata', 'Lütfen İşçi ID Giriniz!')
            return

        try:
            save_attendance(int(user_id), date, status)
            QMessageBox.information(self, 'Başarılı', 'Devam durumu kaydedildi!')
        except ValueError:
            QMessageBox.warning(self, 'Hata', 'Geçerli bir İşçi ID giriniz!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Tema renkleri
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))  # Arka plan rengini koyu gri yapıyoruz
    palette.setColor(QPalette.WindowText, Qt.white)  # Metin rengini beyaz yapıyoruz
    app.setPalette(palette)

    # İşçi/Formen Panelini göster
    window = WorkerForemanPanel()
    window.show()
    sys.exit(app.exec_())
