import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                           QTableWidget, QTableWidgetItem, QMessageBox)
import sqlite3
from datetime import datetime

class TarlaYonetimSistemi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tarla Yönetim Sistemi")
        self.setGeometry(100, 100, 800, 600)
        
        # Veritabanı bağlantısı
        self.conn = sqlite3.connect(r"veritabanları\TARLA.db")
        self.cursor = self.conn.cursor()
        self.veritabani_olustur()
        
        # Ana widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Form alanları
        self.form_layout = QHBoxLayout()
        
        # Tarla bilgileri
        self.tarla_adi = QLineEdit()
        self.tarla_adi.setPlaceholderText("Tarla Adı")
        self.alan = QLineEdit()
        self.alan.setPlaceholderText("Alan (Dönüm)")
        self.urun = QLineEdit()
        self.urun.setPlaceholderText("Ekili Ürün")
        
        self.form_layout.addWidget(self.tarla_adi)
        self.form_layout.addWidget(self.alan)
        self.form_layout.addWidget(self.urun)
        
        # Butonlar
        self.ekle_btn = QPushButton("Tarla Ekle")
        self.ekle_btn.clicked.connect(self.tarla_ekle)
        self.guncelle_btn = QPushButton("Güncelle")
        self.guncelle_btn.clicked.connect(self.tarla_guncelle)
        self.sil_btn = QPushButton("Sil")
        self.sil_btn.clicked.connect(self.tarla_sil)
        
        self.form_layout.addWidget(self.ekle_btn)
        self.form_layout.addWidget(self.guncelle_btn)
        self.form_layout.addWidget(self.sil_btn)
        
        self.layout.addLayout(self.form_layout)
        
        # Tablo
        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Tarla Adı", "Alan (Dönüm)", "Ekili Ürün", "Son Güncelleme"])
        self.tablo.clicked.connect(self.tablo_secim)
        self.layout.addWidget(self.tablo)
        
        self.tarlalari_listele()
    
    def veritabani_olustur(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarlalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarla_adi TEXT NOT NULL,
                alan REAL NOT NULL,
                urun TEXT,
                son_guncelleme TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def tarla_ekle(self):
        try:
            tarla_adi = self.tarla_adi.text()
            alan = float(self.alan.text())
            urun = self.urun.text()
            
            if not tarla_adi or not alan:
                QMessageBox.warning(self, "Uyarı", "Tarla adı ve alan zorunludur!")
                return
            
            self.cursor.execute('''
                INSERT INTO tarlalar (tarla_adi, alan, urun, son_guncelleme)
                VALUES (?, ?, ?, ?)
            ''', (tarla_adi, alan, urun, datetime.now()))
            
            self.conn.commit()
            self.tarlalari_listele()
            self.formu_temizle()
            
            QMessageBox.information(self, "Başarılı", "Tarla başarıyla eklendi!")
            
        except ValueError:
            QMessageBox.warning(self, "Hata", "Alan sayısal bir değer olmalıdır!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")
    
    def tarla_guncelle(self):
        try:
            secili_satir = self.tablo.currentRow()
            if secili_satir < 0:
                QMessageBox.warning(self, "Uyarı", "Lütfen güncellenecek tarlayı seçin!")
                return
            
            tarla_id = int(self.tablo.item(secili_satir, 0).text())
            tarla_adi = self.tarla_adi.text()
            alan = float(self.alan.text())
            urun = self.urun.text()
            
            if not tarla_adi or not alan:
                QMessageBox.warning(self, "Uyarı", "Tarla adı ve alan zorunludur!")
                return
            
            self.cursor.execute('''
                UPDATE tarlalar 
                SET tarla_adi = ?, alan = ?, urun = ?, son_guncelleme = ?
                WHERE id = ?
            ''', (tarla_adi, alan, urun, datetime.now(), tarla_id))
            
            self.conn.commit()
            self.tarlalari_listele()
            self.formu_temizle()
            
            QMessageBox.information(self, "Başarılı", "Tarla başarıyla güncellendi!")
            
        except ValueError:
            QMessageBox.warning(self, "Hata", "Alan sayısal bir değer olmalıdır!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu: {str(e)}")
    
    def tarla_sil(self):
        secili_satir = self.tablo.currentRow()
        if secili_satir < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek tarlayı seçin!")
            return
        
        tarla_id = int(self.tablo.item(secili_satir, 0).text())
        
        cevap = QMessageBox.question(self, "Onay", 
                                   "Bu tarlayı silmek istediğinizden emin misiniz?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
        
        if cevap == QMessageBox.StandardButton.Yes:
            try:
                self.cursor.execute("DELETE FROM tarlalar WHERE id = ?", (tarla_id,))
                self.conn.commit()
                self.tarlalari_listele()
                self.formu_temizle()
                QMessageBox.information(self, "Başarılı", "Tarla başarıyla silindi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Silme işlemi başarısız: {str(e)}")
    
    def tarlalari_listele(self):
        self.cursor.execute("SELECT * FROM tarlalar ORDER BY id DESC")
        tarlalar = self.cursor.fetchall()
        
        self.tablo.setRowCount(len(tarlalar))
        
        for row, tarla in enumerate(tarlalar):
            for col, veri in enumerate(tarla):
                item = QTableWidgetItem(str(veri))
                self.tablo.setItem(row, col, item)
    
    def tablo_secim(self):
        secili_satir = self.tablo.currentRow()
        self.tarla_adi.setText(self.tablo.item(secili_satir, 1).text())
        self.alan.setText(self.tablo.item(secili_satir, 2).text())
        self.urun.setText(self.tablo.item(secili_satir, 3).text())
    
    def formu_temizle(self):
        self.tarla_adi.clear()
        self.alan.clear()
        self.urun.clear()
    
    def closeEvent(self, event):
        self.conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pencere = TarlaYonetimSistemi()
    pencere.show()
    sys.exit(app.exec())