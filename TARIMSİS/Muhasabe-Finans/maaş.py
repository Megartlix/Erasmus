import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from datetime import datetime

class MaasYonetimProgrami(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.db_connection()

    def initUI(self):
        self.setWindowTitle('İşçi Maaş Yönetim Programı')
        self.setGeometry(100, 100, 500, 400)
        
        # Modern font ve renkler
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f9;
                font-family: 'Roboto', sans-serif;
                color: #333;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            QComboBox, QLineEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #5c6bc0;
                color: #fff;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3f51b5;
            }
            QTableWidget {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QTableWidgetItem {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #dce2f7;
            }
        """)

        layout = QVBoxLayout()
        
        # Kullanıcı Seçimi
        self.kullaniciComboBox = QComboBox()
        self.kullaniciComboBox.currentIndexChanged.connect(self.select_kullanici)
        layout.addWidget(QLabel('Kullanıcı Seçin:'))
        layout.addWidget(self.kullaniciComboBox)
        
        # Maaş Girişi
        self.maasLineEdit = QLineEdit()
        layout.addWidget(QLabel('Maaş Girin:'))
        layout.addWidget(self.maasLineEdit)
        
        # Maaş Yatırma butonu
        self.yatirButton = QPushButton('Maaş Yatır')
        self.yatirButton.clicked.connect(self.maas_yatir)
        layout.addWidget(self.yatirButton)
        
        # Maaş ödemeleri geçmişini gösterme
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Kullanıcı Adı', 'Maaş', 'Tarih'])
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def db_connection(self):
        """Kullanıcılar ve maaş ödemeleri veritabanlarına bağlanma."""
        # Kullanıcılar veritabanı bağlantısı
        self.conn_kullanici = sqlite3.connect('veritabanları\kullanicilar.db')
        self.cursor_kullanici = self.conn_kullanici.cursor()
        
        # Maaş ödemeleri veritabanı bağlantısı
        self.conn_odeme = sqlite3.connect(r'veritabanları\maaş.db')
        self.cursor_odeme = self.conn_odeme.cursor()
        
        # Kullanıcıları al ve ComboBox'a ekle
        self.cursor_kullanici.execute("SELECT kullanici_adi FROM kullanicilar")
        users = self.cursor_kullanici.fetchall()
        
        for user in users:
            self.kullaniciComboBox.addItem(user[0])

    def select_kullanici(self):
        """Kullanıcı seçildiğinde maaş ödeme geçmişini göster."""
        selected_user = self.kullaniciComboBox.currentText()
        
        # Kullanıcıya ait maaş ödemelerini sorgula
        self.cursor_odeme.execute("SELECT kullanici_adi, maas, tarih FROM odemeler WHERE kullanici_adi=?", (selected_user,))
        payments = self.cursor_odeme.fetchall()
        
        self.table.setRowCount(0)
        for row, payment in enumerate(payments):
            self.table.insertRow(row)
            for col, data in enumerate(payment):
                self.table.setItem(row, col, QTableWidgetItem(str(data)))
    
    def maas_yatir(self):
        """Maaş yatırma işlemi."""
        selected_user = self.kullaniciComboBox.currentText()
        maas = self.maasLineEdit.text()
        
        if selected_user and maas:
            # Maaş yatırma tarihini al
            tarih = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Maaşı maaş ödemeleri veritabanına kaydet
            self.cursor_odeme.execute("INSERT INTO odemeler (kullanici_adi, maas, tarih) VALUES (?, ?, ?)", 
                                       (selected_user, maas, tarih))
            self.conn_odeme.commit()
            
            # Ödeme geçmişini güncelle
            self.select_kullanici()
            self.maasLineEdit.clear()
            
            print(f'{selected_user} için {maas} TL maaş yatırıldı.')
        else:
            print("Kullanıcı veya maaş bilgisi eksik!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MaasYonetimProgrami()
    window.show()
    sys.exit(app.exec_())
