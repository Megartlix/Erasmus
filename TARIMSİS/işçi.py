import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QWidget, QFormLayout, 
                             QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

# Veritabanı dosyasının ismi
DB_NAME_USERS = 'veritabanları\kullanicilar.db'  # Kullanıcılar veritabanı
DB_NAME_TASKS = 'veritabanları\gorevler.db'      # Görevler veritabanı

# Veritabanına görevi tamamladığını kaydeden fonksiyon
def complete_task_in_db(task_id, user_id):
    try:
        conn = sqlite3.connect(DB_NAME_TASKS)
        cursor = conn.cursor()

        # 'Yapılmadı' olan görevi 'Yapıldı' olarak güncelle
        cursor.execute("""
            UPDATE gorevler
            SET onay_durumu = 'Yapıldı', kullanici_id = ?
            WHERE id = ?
        """, (user_id, task_id))  # Durumu 'Yapıldı' olarak güncelliyoruz

        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Veritabanı hatası: {e}")
        raise e

# İşçi Görev Ekranı
class WorkerTaskScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('İşçi Görev Ekranı')
        self.setGeometry(300, 150, 800, 600)
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")

        # Ana layout
        main_layout = QVBoxLayout()

        # Başlık
        self.header_label = QLabel('İşçi Görev Ekranı')
        self.header_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.header_label)

        # Kullanıcı giriş alanları
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Kullanıcı ID'si")
        self.user_id_input.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setStyleSheet("""
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
        self.login_button.clicked.connect(self.login)

        # Kullanıcı bilgilerini saklayacak değişkenler
        self.logged_in_user_id = None
        self.logged_in_user_name = None

        # Görev Tablosu
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)  # 5 sütun + 1 buton sütunu
        self.task_table.setHorizontalHeaderLabels(['Görev Adı', 'Görev Kodu', 'Açıklama', 'Tarih', 'Durum', 'Durum Güncelle'])
        self.task_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.task_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.task_table.setStyleSheet("background-color: #444444; color: #FFFFFF;")

        # Form Layout
        form_layout = QFormLayout()
        form_layout.addRow(self.user_id_input)
        form_layout.addRow(self.login_button)

        # Ana Layout'a ekleyelim
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.task_table)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def login(self):
        user_id = self.user_id_input.text().strip()

        if not user_id.isdigit():
            QMessageBox.warning(self, 'Hata', 'Geçersiz kullanıcı ID\'si.')
            return

        # Kullanıcı ID'sini veritabanından kontrol et
        conn = sqlite3.connect(DB_NAME_USERS)
        cursor = conn.cursor()
        cursor.execute("SELECT id, kullanici_adi FROM kullanicilar WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.logged_in_user_id = user[0]
            self.logged_in_user_name = user[1]
            QMessageBox.information(self, 'Başarı', f'Hoş geldiniz, {self.logged_in_user_name}!')
            self.load_tasks()
        else:
            QMessageBox.warning(self, 'Hata', 'Geçersiz kullanıcı ID.')

    def load_tasks(self):
        try:
            # Kullanıcıya ait görevleri veritabanından al
            conn = sqlite3.connect(DB_NAME_TASKS)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, gorev_adi, gorev_kodu, gorev_aciklamasi, tarih, onay_durumu 
                FROM gorevler
                WHERE kullanici_id IS NULL OR kullanici_id = ?
            """, (self.logged_in_user_id,))  # Burada yalnızca atanmış görevler çekilecek
            tasks = cursor.fetchall()
            conn.close()

            # Görevleri tabloya ekleyelim
            self.task_table.setRowCount(0)  # Önceki verileri temizle
            for task in tasks:
                row_position = self.task_table.rowCount()
                self.task_table.insertRow(row_position)
                self.task_table.setItem(row_position, 0, QTableWidgetItem(task[1]))  # Görev Adı
                self.task_table.setItem(row_position, 1, QTableWidgetItem(task[2]))  # Görev Kodu
                self.task_table.setItem(row_position, 2, QTableWidgetItem(task[3]))  # Görev Açıklaması
                self.task_table.setItem(row_position, 3, QTableWidgetItem(task[4]))  # Tarih

                # Durumu doğru şekilde göster
                status = task[5] if task[5] != 'Yapılmadı' else 'Onaylanmadı'
                self.task_table.setItem(row_position, 4, QTableWidgetItem(status))  # Durum

                # Durum güncelleme butonu
                update_button = QPushButton("Durumu Yapıldı'ya Çek")
                update_button.clicked.connect(lambda checked, task_id=task[0]: self.update_task_status(task_id))
                self.task_table.setCellWidget(row_position, 5, update_button)

        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            QMessageBox.warning(self, 'Hata', f"Veritabanı hatası: {e}")

    def update_task_status(self, task_id):
        try:
            # Görev tamamlandığında veritabanında güncelleme
            complete_task_in_db(task_id, self.logged_in_user_id)
            self.load_tasks()  # Güncellenen görevleri tekrar yükle

            QMessageBox.information(self, 'Görev Tamamlandı', f'Görev {task_id} durumu "Yapıldı" olarak güncellendi!')
        except Exception as e:
            QMessageBox.warning(self, 'Hata', f"Görev tamamlanırken bir hata oluştu: {e}")

# PyQt5 uygulamasını başlat
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Tema renkleri
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)

    # İşçi Görev Ekranını başlat
    window = WorkerTaskScreen()
    window.show()
    sys.exit(app.exec_())
