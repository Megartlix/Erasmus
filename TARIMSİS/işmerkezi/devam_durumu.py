import sys
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,
                             QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPalette, QColor, QFont
from openpyxl import Workbook

# Veritabanı dosyaları
DB_NAME_USERS = r"veritabanları\kullanicilar.db"
DB_NAME_ATTENDANCE = r"veritabanları\devamagadevam.db"

# Devamsızlık verilerini yükleme
def get_attendance_data():
    conn = sqlite3.connect(DB_NAME_ATTENDANCE)
    cursor = conn.cursor()
    cursor.execute("SELECT kullanici_id, tarih, durum FROM devamsizliklar")
    data = cursor.fetchall()
    conn.close()
    return data

# Kullanıcı isimlerini ID'lerine göre alma
def get_user_name(user_id):
    conn = sqlite3.connect(DB_NAME_USERS)
    cursor = conn.cursor()
    cursor.execute("SELECT kullanici_adi FROM kullanicilar WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Bilinmeyen"

# Devamsızlık verilerini Excel'e kaydetme
def save_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Devamsızlık Verileri"
    sheet.append(["Kullanıcı ID", "Kullanıcı Adı", "Tarih", "Durum"])
    for record in data:
        user_id, tarih, durum = record
        user_name = get_user_name(user_id)
        sheet.append([user_id, user_name, tarih, durum])
    file_path, _ = QFileDialog.getSaveFileName(None, "Excel Dosyası Kaydet", "", "Excel Files (*.xlsx)")
    if file_path:
        workbook.save(file_path)
        QMessageBox.information(None, "Başarılı", "Veriler başarıyla Excel dosyasına aktarıldı!")

# Devam performansını grafik olarak çizme
def plot_performance(data):
    users = {}
    for user_id, tarih, durum in data:
        if user_id not in users:
            users[user_id] = {'Geldi': 0, 'İzinli': 0, 'Gelmedi': 0}
        users[user_id][durum] += 1
    user_names = [get_user_name(user_id) for user_id in users.keys()]
    attendance_data = [users[user_id]['Geldi'] for user_id in users.keys()]
    absent_data = [users[user_id]['Gelmedi'] for user_id in users.keys()]
    leave_data = [users[user_id]['İzinli'] for user_id in users.keys()]

    fig, ax = plt.subplots()
    index = range(len(user_names))
    bar_width = 0.2
    ax.bar(index, attendance_data, bar_width, label='Geldi')
    ax.bar([i + bar_width for i in index], leave_data, bar_width, label='İzinli')
    ax.bar([i + 2 * bar_width for i in index], absent_data, bar_width, label='Gelmedi')
    ax.set_xlabel('İşçiler')
    ax.set_ylabel('Sayısı')
    ax.set_title('İşçilerin Devam Performansı')
    ax.set_xticks([i + bar_width for i in index])
    ax.set_xticklabels(user_names, rotation=45)
    ax.legend()
    plt.tight_layout()
    plt.show()

# Basit tahmin modeli
def ai_suggestion(data):
    dates = []
    absences = []
    for user_id, tarih, durum in data:
        if durum == "Gelmedi":
            dates.append(int(tarih.replace("-", "")))
            absences.append(1)
        else:
            dates.append(int(tarih.replace("-", "")))
            absences.append(0)
    if len(dates) < 2:
        QMessageBox.information(None, "Öneri", "Yeterli veri yok, öneri yapılamıyor.")
        return
    # Ortalama devamsızlık oranı
    average_absence = np.mean(absences)
    suggestion = "Yarın devamsızlık riski düşük görünüyor." if average_absence < 0.5 else "Dikkat! Yarın devamsızlık riski yüksek olabilir."
    QMessageBox.information(None, "Öneri", suggestion)

# Admin Paneli
class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Admin Paneli')
        self.setGeometry(400, 200, 600, 500)
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")
        main_layout = QVBoxLayout()
        self.header_label = QLabel('Admin Paneli')
        self.header_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.header_label)

        # Devamsızlıkları görme butonu
        self.show_attendance_button = QPushButton('Devamsızlıkları Gör')
        self.show_attendance_button.setStyleSheet(self.button_style())
        self.show_attendance_button.clicked.connect(self.show_attendance)
        main_layout.addWidget(self.show_attendance_button)

        # Performans grafiğini gösterme butonu
        self.show_graph_button = QPushButton('Devam Performansı Grafiği')
        self.show_graph_button.setStyleSheet(self.button_style())
        self.show_graph_button.clicked.connect(self.show_performance_graph)
        main_layout.addWidget(self.show_graph_button)

        # Yapay zeka önerisi butonu
        self.ai_suggestion_button = QPushButton('Yapay Zeka Önerisi')
        self.ai_suggestion_button.setStyleSheet(self.button_style())
        self.ai_suggestion_button.clicked.connect(self.show_ai_suggestion)
        main_layout.addWidget(self.ai_suggestion_button)

        # Excel'e aktar butonu
        self.export_excel_button = QPushButton('Excel\'e Aktar')
        self.export_excel_button.setStyleSheet(self.button_style())
        self.export_excel_button.clicked.connect(self.export_to_excel)
        main_layout.addWidget(self.export_excel_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def button_style(self):
        return """
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
        """

    def show_attendance(self):
        data = get_attendance_data()
        attendance_table = QTableWidget()
        attendance_table.setColumnCount(4)
        attendance_table.setHorizontalHeaderLabels(["Kullanıcı ID", "Kullanıcı Adı", "Tarih", "Durum"])
        attendance_table.setRowCount(len(data))

        for row, (user_id, tarih, durum) in enumerate(data):
            attendance_table.setItem(row, 0, QTableWidgetItem(str(user_id)))
            attendance_table.setItem(row, 1, QTableWidgetItem(get_user_name(user_id)))
            attendance_table.setItem(row, 2, QTableWidgetItem(tarih))
            attendance_table.setItem(row, 3, QTableWidgetItem(durum))

        attendance_window = QMainWindow(self)
        attendance_window.setWindowTitle('Devamsızlıklar')
        attendance_window.setGeometry(450, 250, 600, 400)
        attendance_window.setCentralWidget(attendance_table)
        attendance_window.show()

    def show_performance_graph(self):
        data = get_attendance_data()
        plot_performance(data)

    def show_ai_suggestion(self):
        data = get_attendance_data()
        ai_suggestion(data)

    def export_to_excel(self):
        data = get_attendance_data()
        save_to_excel(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())
