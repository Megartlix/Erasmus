import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QWidget, QFormLayout, 
                             QComboBox, QTextEdit, QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor

# Veritabanı dosyasının ismi
DB_NAME_USERS = r'veritabanları\kullanicilar.db'  # Kullanıcılar veritabanı
DB_NAME_TASKS = r'veritabanları\gorevler.db'      # Görevler veritabanı

# Veritabanına görev ekleme fonksiyonu (gorevler.db)
def add_task_to_db(user_id, task_name, task_code, task_description, task_date):
    try:
        conn = sqlite3.connect(DB_NAME_TASKS)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO gorevler (kullanici_id, gorev_adi, gorev_kodu, gorev_aciklamasi, tarih, onay_durumu) 
            VALUES (?, ?, ?, ?, ?, 'Yapılmadı')  -- 'Yapılmadı' varsayılan değer
        """, (user_id, task_name, task_code, task_description, task_date))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        raise e

# Görev Verme Ekranı
class TaskAssignmentScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Görev Verme')
        self.setGeometry(300, 150, 400, 450)
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")

        # Ana layout
        main_layout = QVBoxLayout()

        # Başlık
        self.header_label = QLabel('Görev Verme Ekranı')
        self.header_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.header_label)

        # Form Layout
        form_layout = QFormLayout()

        # Kullanıcı seçimi (işçi veya formen)
        self.user_select_combo = QComboBox()
        self.user_select_combo.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.user_select_combo.addItem("Seçiniz...")
        self.load_users()

        # Görev adı ve kodu için input alanları
        self.task_name_input = QLineEdit()
        self.task_name_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.task_name_input.setPlaceholderText("Görev Adı")

        self.task_code_input = QLineEdit()
        self.task_code_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.task_code_input.setPlaceholderText("Görev Kodu")

        # Görev açıklaması için QTextEdit alanı
        self.task_description_input = QTextEdit()
        self.task_description_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.task_description_input.setPlaceholderText("Görev Açıklaması")

        # Görev tarihi seçimi
        self.task_date_input = QDateEdit(QDate.currentDate())
        self.task_date_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.task_date_input.setDisplayFormat("yyyy-MM-dd")
        self.task_date_input.setCalendarPopup(True)

        form_layout.addRow('Kullanıcı Seç:', self.user_select_combo)
        form_layout.addRow('Görev Adı:', self.task_name_input)
        form_layout.addRow('Görev Kodu:', self.task_code_input)
        form_layout.addRow('Görev Açıklaması:', self.task_description_input)
        form_layout.addRow('Tarih:', self.task_date_input)

        # Görev Ver butonu
        self.assign_button = QPushButton('Görev Ver')
        self.assign_button.setStyleSheet("""
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
        self.assign_button.clicked.connect(self.assign_task)

        # Form ve butonu layout'a ekleyelim
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.assign_button)

        # Merkezi widget olarak ayarlama
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_users(self):
        """Kullanıcıları veritabanından yükler ve combobox'a ekler."""
        try:
            conn = sqlite3.connect(DB_NAME_USERS)
            cursor = conn.cursor()
            cursor.execute("SELECT id, kullanici_adi FROM kullanicilar WHERE rol IN ('işçi', 'formen')")
            users = cursor.fetchall()
            for user in users:
                self.user_select_combo.addItem(user[1], user[0])  # Kullanıcı adı ve id'si
            conn.close()
        except sqlite3.Error as e:
            QMessageBox.warning(self, 'Hata', f"Veritabanı hatası: {e}")

    def assign_task(self):
        """Kullanıcıdan alınan bilgileri veritabanına kaydeder."""
        # Kullanıcıdan alınan veriler
        user_id = self.user_select_combo.currentData()
        task_name = self.task_name_input.text().strip()
        task_code = self.task_code_input.text().strip()
        task_description = self.task_description_input.toPlainText().strip()
        task_date = self.task_date_input.text().strip()

        # Gerekli alanların dolu olup olmadığını kontrol et
        if not user_id or not task_name or not task_code or not task_description or not task_date:
            QMessageBox.warning(self, 'Hata', 'Lütfen tüm alanları doldurun!')
            return

        # Veritabanına görevi ekle
        try:
            add_task_to_db(user_id, task_name, task_code, task_description, task_date)
            QMessageBox.information(self, 'Başarılı', 'Görev başarıyla verildi!')
            self.clear_fields()
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f'Görev verilirken bir hata oluştu: {e}')

    def clear_fields(self):
        """Giriş alanlarını temizler."""
        self.user_select_combo.setCurrentIndex(0)
        self.task_name_input.clear()
        self.task_code_input.clear()
        self.task_description_input.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Tema renkleri
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    # Görev Verme ekranını göster
    window = TaskAssignmentScreen()
    window.show()
    sys.exit(app.exec_())
