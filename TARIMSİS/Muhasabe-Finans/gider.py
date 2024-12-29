import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QFont, QColor, QPalette

class GiderHesaplaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gider Hesaplama")
        self.setGeometry(100, 100, 400, 300)

        # Modern tema için renkler ve yazı tipini ayarlama
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: white;
                font-family: Arial, sans-serif;
                font-size: 12pt;
            }
            QLabel {
                font-weight: bold;
                color: #f1f1f1;
            }
            QLineEdit {
                background-color: #444444;
                border: 2px solid #666666;
                color: white;
                padding: 5px;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #007BFF;
                border: none;
                color: white;
                padding: 10px;
                font-size: 14px;
                border-radius: 8px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QVBoxLayout {
                margin: 20px;
            }
        """)

        # UI elemanları
        self.layout = QVBoxLayout()

        # Vergi oranı girişi
        self.vergi_label = QLabel("Vergi Oranı (%):", self)
        self.vergi_orani_input = QLineEdit(self)
        self.layout.addWidget(self.vergi_label)
        self.layout.addWidget(self.vergi_orani_input)

        # Detaylı gider gösterimi için labellar
        self.alim_label = QLabel("Alım Giderleri: ", self)
        self.yem_label = QLabel("Yem Giderleri: ", self)
        self.maas_label = QLabel("Maaş Giderleri: ", self)
        self.vergi_total_label = QLabel("Toplam Vergi: ", self)
        self.result_label = QLabel("Toplam Gider: ", self)

        self.layout.addWidget(self.alim_label)
        self.layout.addWidget(self.yem_label)
        self.layout.addWidget(self.maas_label)
        self.layout.addWidget(self.vergi_total_label)
        self.layout.addWidget(self.result_label)

        # Gideri hesapla butonu
        self.calculate_button = QPushButton("Gideri Hesapla", self)
        self.calculate_button.clicked.connect(self.calculate_gider)
        self.layout.addWidget(self.calculate_button)

        # Gideri kaydet butonu
        self.save_button = QPushButton("Kaydet", self)
        self.save_button.clicked.connect(self.save_gider)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def connect_db(self, db_name):
        """Veritabanına bağlanma fonksiyonu"""
        try:
            conn = sqlite3.connect(db_name)
            return conn.cursor(), conn
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı bağlantı hatası: {e}")
            return None, None

    def create_giderler_table(self):
        """Giderler tablosunu oluşturma fonksiyonu"""
        cursor, conn = self.connect_db('veritabanları/giderler.db')
        if cursor:
            try:
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS giderler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ay TEXT NOT NULL,
                    toplam_gider REAL NOT NULL,
                    alim_gider REAL NOT NULL,
                    yem_gider REAL NOT NULL,
                    maas_gider REAL NOT NULL,
                    vergi_gider REAL NOT NULL,
                    kayit_tarihi DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                conn.commit()
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Hata", f"Tablo oluşturma hatası: {e}")
            finally:
                conn.close()

    def get_yem_giderleri(self):
        """Yem veritabanından toplam gideri hesapla"""
        try:
            cursor, conn = self.connect_db('yem_besleme.db')
            if cursor:
                cursor.execute("SELECT miktar_kg, fiyat FROM yem")
                yem_verileri = cursor.fetchall()
                conn.close()
                
                toplam_yem_gideri = sum(miktar * fiyat for miktar, fiyat in yem_verileri)
                return toplam_yem_gideri
            return 0
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Uyarı", f"Yem giderleri hesaplanırken hata: {e}")
            return 0

    def calculate_gider(self):
        try:
            # Kullanıcıdan vergi oranını al
            vergi_orani = float(self.vergi_orani_input.text()) / 100

            # Alımlar DB'den verileri al
            alimlar_cursor, alimlar_conn = self.connect_db('veritabanları/alimlar.db')
            if alimlar_cursor:
                alimlar_cursor.execute("SELECT urun_fiyati FROM alimlar")
                urun_fiyatlari = alimlar_cursor.fetchall()
                alimlar_conn.close()
                toplam_alim = sum([urun[0] for urun in urun_fiyatlari])
            else:
                toplam_alim = 0

            # Yem giderlerini al
            toplam_yem = self.get_yem_giderleri()

            # Maaşlar DB'den maaş verilerini al
            maaslar_cursor, maaslar_conn = self.connect_db('veritabanları/maaş.db')
            if maaslar_cursor:
                ay = QDate.currentDate().toString("yyyy-MM")
                maaslar_cursor.execute("SELECT maas FROM odemeler WHERE tarih LIKE ?", (f"{ay}%",))
                maaslar = maaslar_cursor.fetchall()
                maaslar_conn.close()
                toplam_maas = sum([maas[0] for maas in maaslar])
            else:
                toplam_maas = 0

            # Vergi hesapla (tüm giderler üzerinden)
            toplam_vergisiz = toplam_alim + toplam_yem + toplam_maas
            vergi = toplam_vergisiz * vergi_orani

            # Toplam gider hesapla
            toplam_gider = toplam_vergisiz + vergi

            # Gider detaylarını göster
            self.alim_label.setText(f"Alım Giderleri: {toplam_alim:.2f} TL")
            self.yem_label.setText(f"Yem Giderleri: {toplam_yem:.2f} TL")
            self.maas_label.setText(f"Maaş Giderleri: {toplam_maas:.2f} TL")
            self.vergi_total_label.setText(f"Toplam Vergi: {vergi:.2f} TL")
            self.result_label.setText(f"Toplam Gider: {toplam_gider:.2f} TL")

            # Kaydedilecek değerleri tut
            self.toplam_gider = toplam_gider
            self.alim_gider = toplam_alim
            self.yem_gider = toplam_yem
            self.maas_gider = toplam_maas
            self.vergi_gider = vergi
            self.ay = ay

        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir vergi oranı giriniz.")

    def save_gider(self):
        """Hesaplanan gideri veritabanına kaydet"""
        if hasattr(self, 'toplam_gider'):
            # Giderler tablosunun var olduğundan emin ol
            self.create_giderler_table()

            try:
                # Gideri giderler veritabanına kaydet
                giderler_cursor, giderler_conn = self.connect_db('veritabanları/giderler.db')
                if giderler_cursor:
                    giderler_cursor.execute("""
                        INSERT INTO giderler 
                        (ay, toplam_gider, alim_gider, yem_gider, maas_gider, vergi_gider) 
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (self.ay, self.toplam_gider, self.alim_gider, 
                         self.yem_gider, self.maas_gider, self.vergi_gider))
                    giderler_conn.commit()
                    giderler_conn.close()
                    
                    QMessageBox.information(self, "Başarılı", f"{self.ay} ayı giderleri başarıyla kaydedildi!")
                    
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Hata", f"Gider kaydedilirken hata oluştu: {e}")
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce gideri hesaplayın!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GiderHesaplaApp()
    window.show()
    sys.exit(app.exec_())