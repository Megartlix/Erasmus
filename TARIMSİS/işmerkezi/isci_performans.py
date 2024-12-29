import sys
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont

# Veritabanı dosyasının ismi
DB_NAME_USERS = r'veritabanları\kullanicilar.db'  # Kullanıcılar veritabanı
DB_NAME_TASKS = r'veritabanları\gorevler.db'      # Görevler veritabanı

# Performans verilerini almak
def get_user_performance():
    conn = sqlite3.connect(DB_NAME_TASKS)
    cursor = conn.cursor()
    cursor.execute("SELECT kullanici_id, gorev_kodu, COUNT(*) as task_count FROM gorevler GROUP BY kullanici_id, gorev_kodu")
    data = cursor.fetchall()
    conn.close()
    return data

# Kullanıcı bilgilerini yükleme
def get_users_by_role(role):
    conn = sqlite3.connect(DB_NAME_USERS)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, kullanici_adi FROM kullanicilar WHERE rol = '{role}'")
    users = cursor.fetchall()
    conn.close()
    return users

# En çok yapılan görev kodu
def get_most_frequent_task():
    conn = sqlite3.connect(DB_NAME_TASKS)
    cursor = conn.cursor()
    cursor.execute("SELECT gorev_kodu, COUNT(*) as task_count FROM gorevler GROUP BY gorev_kodu ORDER BY task_count DESC LIMIT 1")
    data = cursor.fetchone()
    conn.close()
    return data

# Yapay Zeka Tavsiyesi
def generate_ai_recommendation(user_id):
    performance_data = get_user_performance()
    user_data = [item for item in performance_data if item[0] == user_id]
    total_tasks = sum([item[2] for item in user_data])
    
    if total_tasks > 50:
        return "Çok başarılı, daha fazla sorumluluk alabilirsiniz!"
    elif total_tasks > 20:
        return "İyi iş çıkarıyorsunuz, daha fazla proje deneyebilirsiniz."
    else:
        return "Daha fazla deneyim kazanmanız faydalı olabilir."

# Performans Grafik Görselleştirmesi (İşçi - İşçi Karşılaştırması)
def plot_comparison_graph(user_data1, user_data2, user_name1, user_name2):
    tasks1 = [item[1] for item in user_data1]
    task_counts1 = [item[2] for item in user_data1]
    
    tasks2 = [item[1] for item in user_data2]
    task_counts2 = [item[2] for item in user_data2]

    # İşçi karşılaştırması grafik tipi
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    index = np.arange(len(tasks1))

    bar1 = ax.bar(index, task_counts1, bar_width, label=user_name1, color='b')
    bar2 = ax.bar(index + bar_width, task_counts2, bar_width, label=user_name2, color='r')

    ax.set_xlabel('Görev Kodu')
    ax.set_ylabel('Görev Sayısı')
    ax.set_title(f'{user_name1} ve {user_name2} Performans Karşılaştırması')
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(tasks1, rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.show()

# Dal-Yaprak Grafiği (Stem-and-Leaf Plot) Görselleştirmesi
def plot_stem_and_leaf(user_data, user_name):
    task_counts = [item[2] for item in user_data]
    task_counts.sort()

    # Dal-Yaprak Grafiği
    stems = [task_counts[i] // 10 for i in range(len(task_counts))]
    leaves = [task_counts[i] % 10 for i in range(len(task_counts))]

    print(f"\n{user_name} İçin Dal-Yaprak Grafiği:")
    for stem in set(stems):
        leaf_values = [str(leaves[i]) for i in range(len(stems)) if stems[i] == stem]
        print(f"{stem}| {' '.join(leaf_values)}")

# Performans Ekranı
class PerformanceScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Performans Takibi')
        self.setGeometry(300, 150, 600, 600)

        # Arka plan ve metin rengi için QPalette kullanımı
        self.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF; font-family: Arial;")

        # Ana layout
        main_layout = QVBoxLayout()

        # Başlık
        self.header_label = QLabel('İşçi ve Formen Performansı')
        self.header_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        self.header_label.setStyleSheet("color: #00CED1;")
        main_layout.addWidget(self.header_label)

        # Kullanıcı rol seçimi
        self.role_select_combo = QComboBox()
        self.role_select_combo.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.role_select_combo.addItem("İşçi", "işçi")
        self.role_select_combo.addItem("Formen", "formen")
        self.role_select_combo.currentTextChanged.connect(self.update_user_combos)
        main_layout.addWidget(self.role_select_combo)

        # Kullanıcı seçimi
        self.user_select_combo1 = QComboBox()
        self.user_select_combo1.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.user_select_combo1.addItem("Seçiniz...")
        
        self.user_select_combo2 = QComboBox()
        self.user_select_combo2.setStyleSheet("background-color: #444444; color: #FFFFFF; padding: 10px; border-radius: 8px;")
        self.user_select_combo2.addItem("Seçiniz...")

        # Performans karşılaştırma butonu
        self.compare_button = QPushButton('İki Kullanıcıyı Karşılaştır')
        self.compare_button.setStyleSheet("""
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
        self.compare_button.clicked.connect(self.compare_users)

        # Yapay Zeka Tavsiyesi gösterim butonu
        self.show_ai_button = QPushButton('Yapay Zeka Tavsiyesi Al')
        self.show_ai_button.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #000000;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF8C00;
            }
        """)
        self.show_ai_button.clicked.connect(self.show_ai_recommendation)

        # En çok yapılan görev butonu
        self.show_most_frequent_task_button = QPushButton('En Çok Yapılan Görev')
        self.show_most_frequent_task_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6347;
                color: #FFFFFF;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF4500;
            }
        """)
        self.show_most_frequent_task_button.clicked.connect(self.show_most_frequent_task)

        # Ana layout'a ekle
        main_layout.addWidget(self.user_select_combo1)
        main_layout.addWidget(self.user_select_combo2)
        main_layout.addWidget(self.compare_button)
        main_layout.addWidget(self.show_ai_button)
        main_layout.addWidget(self.show_most_frequent_task_button)

        # Merkezi widget olarak ayarlama
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_users(self, role):
        return get_users_by_role(role)

    def update_user_combos(self):
        role = self.role_select_combo.currentData()
        if not role:
            return
        
        # Kullanıcıları yükle
        users = self.load_users(role)
        self.user_select_combo1.clear()
        self.user_select_combo2.clear()

        self.user_select_combo1.addItem("Seçiniz...")
        self.user_select_combo2.addItem("Seçiniz...")

        for user_id, user_name in users:
            # ID ve isimleri ComboBox'a ekleyelim
            self.user_select_combo1.addItem(f"{user_id} - {user_name}", user_id)
            self.user_select_combo2.addItem(f"{user_id} - {user_name}", user_id)

    def compare_users(self):
        user1_id = self.user_select_combo1.currentData()
        user2_id = self.user_select_combo2.currentData()

        if not user1_id or not user2_id:
            QMessageBox.warning(self, 'Hata', 'Lütfen iki kullanıcı seçin!')
            return

        # Performans verilerini al
        performance_data = get_user_performance()
        user1_data = [item for item in performance_data if item[0] == user1_id]
        user2_data = [item for item in performance_data if item[0] == user2_id]

        # Performans karşılaştırmasını çiz
        plot_comparison_graph(user1_data, user2_data, self.user_select_combo1.currentText(), self.user_select_combo2.currentText())

    def show_ai_recommendation(self):
        user_id = self.user_select_combo1.currentData()
        if not user_id:
            QMessageBox.warning(self, 'Hata', 'Lütfen bir kullanıcı seçin!')
            return

        recommendation = generate_ai_recommendation(user_id)
        QMessageBox.information(self, 'Yapay Zeka Tavsiyesi', recommendation)

    def show_most_frequent_task(self):
        task = get_most_frequent_task()
        if task:
            QMessageBox.information(self, 'En Çok Yapılan Görev', f"En çok yapılan görev: {task[0]} ({task[1]} kere)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Tema renkleri
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(42, 42, 42))  # Arka plan rengini koyu gri yapıyoruz
    palette.setColor(QPalette.WindowText, Qt.white)  # Metin rengini beyaz yapıyoruz
    app.setPalette(palette)

    # Performans ekranını göster
    window = PerformanceScreen()
    window.show()
    sys.exit(app.exec())
