import sys
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel, QDialog, QLineEdit, QFileDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Veritabanı bağlantısı ve ürünleri çekme
def urunleri_raf_bilgisinden_al(raf_numarasi):
    conn = sqlite3.connect(r'veritabanları\inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE shelf_number = ?", (raf_numarasi,))
    urunler = cursor.fetchall()
    conn.close()
    return urunler

def urun_barkod_ile_al(barkod):
    conn = sqlite3.connect(r'veritabanları\inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barkod,))
    urun = cursor.fetchone()
    conn.close()
    return urun

def butun_urunleri_al():
    conn = sqlite3.connect(r'veritabanları\inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    urunler = cursor.fetchall()
    conn.close()
    return urunler

def butun_raf_numaralarini_al():
    conn = sqlite3.connect(r'veritabanları\inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT shelf_number FROM products")
    raflar = cursor.fetchall()
    conn.close()
    return raflar

# Ürün yer değiştirme fonksiyonu
def urun_yer_degistir(barkod, yeni_raf_numarasi):
    conn = sqlite3.connect('veritabanları\inventory.db')
    cursor = conn.cursor()

    # Ürün mevcut mu kontrol et
    cursor.execute("SELECT * FROM products WHERE barcode = ?", (barkod,))
    urun = cursor.fetchone()

    if urun:
        # Ürünün yeni raf numarasını güncelle
        cursor.execute("UPDATE products SET shelf_number = ? WHERE barcode = ?", (yeni_raf_numarasi, barkod))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

# Excel raporu oluşturma fonksiyonu
def rapor_olustur(rapor_turu):
    if rapor_turu == "urun":
        # Ürün raporu oluştur
        urunler = butun_urunleri_al()
        df = pd.DataFrame(urunler, columns=["ID", "Ad", "Barkod", "Miktar", "Giriş Tarihi", "Raf Numarası", "Resim Yolu"])
        
        # Dosya kaydetme penceresi
        dosya_adi, _ = QFileDialog.getSaveFileName(None, "Ürün Raporunu Kaydet", "", "Excel Dosyaları (*.xlsx);;Tüm Dosyalar (*)")
        if dosya_adi:
            df.to_excel(dosya_adi, index=False)
            QMessageBox.information(None, "Rapor Başarıyla Oluşturuldu", f"Ürün raporu {dosya_adi} olarak kaydedildi.", QMessageBox.Ok)
    
    elif rapor_turu == "raf":
        # Raf raporu oluştur
        raflar = butun_raf_numaralarini_al()
        veri = []
        for raf in raflar:
            raf_numarasi = raf[0]
            urunler = urunleri_raf_bilgisinden_al(raf_numarasi)
            for urun in urunler:
                veri.append([raf_numarasi, urun[1], urun[3]])  # Raf No, Ürün Adı, Miktar
        df = pd.DataFrame(veri, columns=["Raf Numarası", "Ürün Adı", "Miktar"])
        
        # Dosya kaydetme penceresi
        dosya_adi, _ = QFileDialog.getSaveFileName(None, "Raf Raporunu Kaydet", "", "Excel Dosyaları (*.xlsx);;Tüm Dosyalar (*)")
        if dosya_adi:
            df.to_excel(dosya_adi, index=False)
            QMessageBox.information(None, "Rapor Başarıyla Oluşturuldu", f"Raf raporu {dosya_adi} olarak kaydedildi.", QMessageBox.Ok)

# Raf bilgisi penceresi
class RafBilgisiPenceresi(QDialog):
    def __init__(self, raf_numarasi):
        super().__init__()

        self.setWindowTitle(f"Raf {raf_numarasi} Bilgileri")
        self.setGeometry(100, 100, 600, 400)

        self.raf_numarasi = raf_numarasi
        self.setStyleSheet("""
            background-color: #1a1a1a;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        """)

        # Layout ve başlık
        layout = QVBoxLayout()

        self.header_label = QLabel(f"Raf {self.raf_numarasi} Ürünleri")
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00C851;")
        layout.addWidget(self.header_label)

        # Ürünleri listele
        self.products_list = QVBoxLayout()

        urunler = urunleri_raf_bilgisinden_al(self.raf_numarasi)
        if urunler:
            for urun in urunler:
                urun_label = QLabel(f"Ürün: {urun[1]}, Miktar: {urun[3]}, Barkod: {urun[2]}")
                self.products_list.addWidget(urun_label)
        else:
            self.products_list.addWidget(QLabel("Bu rafta ürün bulunmamaktadır."))

        layout.addLayout(self.products_list)

        # Kapatma butonu
        close_button = QPushButton("Kapat")
        close_button.setStyleSheet("""
            background-color: #ff3b3b;
            color: white;
            font-size: 18px;
            border-radius: 10px;
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

# Ana pencere
class AnaPencere(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TARIMSİS DEPO KONTROL")
        self.setGeometry(100, 100, 1200, 800)

        # Tasarım: Koyu arka plan, yeşil ve beyaz vurgular
        self.setStyleSheet("""
            background-color: #1a1a1a;
            color: white;
            font-family: 'Segoe UI', sans-serif;
        """)

        # Ana layout
        ana_layout = QVBoxLayout()

        # Başlık
        header_label = QLabel("TARIMSİS DEPO KONTROL")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #00C851;")
        ana_layout.addWidget(header_label)

        # Arama kutusu
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Barkodla ürün ara...")
        self.search_bar.setStyleSheet("""
            padding: 10px; 
            border-radius: 10px; 
            font-size: 18px; 
            background-color: #444; 
            color: white;
        """)
        self.search_bar.textChanged.connect(self.urun_ara)
        ana_layout.addWidget(self.search_bar)

        # Arama Sonuçları
        self.search_result_label = QLabel("Ürün bilgisi buraya gelecek...")
        self.search_result_label.setStyleSheet("font-size: 20px; color: #00C851;")
        self.search_result_label.setWordWrap(True)
        self.search_result_label.setAlignment(Qt.AlignCenter)
        ana_layout.addWidget(self.search_result_label)

        # Raflar için grid layout
        grid_layout = QGridLayout()

        # 14 raf kartı
        self.shelf_buttons = []
        for i in range(1, 15):
            shelf_button = QPushButton(f"Raf {i}")
            shelf_button.setStyleSheet("""
                background-color: #3e8e41; 
                color: white; 
                border-radius: 15px; 
                font-size: 18px;
                padding: 20px;
                margin: 10px;
                text-align: center;
                transition: background-color 0.3s ease;
            """)
            shelf_button.setFixedSize(180, 180)
            shelf_button.clicked.connect(self.raf_bilgisi_penceresini_ac(i))
            self.shelf_buttons.append(shelf_button)
            grid_layout.addWidget(shelf_button, (i-1)//4, (i-1)%4)

        ana_layout.addLayout(grid_layout)

        # Ürün yer değiştirme butonu
        self.yer_degistirme_button = QPushButton("Ürün Yer Değiştirme")
        self.yer_degistirme_button.setStyleSheet("""
            background-color: #00C851; 
            color: white; 
            font-size: 18px; 
            border-radius: 10px;
        """)
        self.yer_degistirme_button.clicked.connect(self.urun_yer_degistir_dialog)
        ana_layout.addWidget(self.yer_degistirme_button)

        # Raporlama butonları
        self.product_report_button = QPushButton("Ürün Raporu Oluştur")
        self.product_report_button.setStyleSheet("""
            background-color: #00C851; 
            color: white; 
            font-size: 18px; 
            border-radius: 10px;
        """)
        self.product_report_button.clicked.connect(lambda: rapor_olustur("urun"))
        
        self.shelf_report_button = QPushButton("Raf Raporu Oluştur")
        self.shelf_report_button.setStyleSheet("""
            background-color: #00C851; 
            color: white; 
            font-size: 18px; 
            border-radius: 10px;
        """)
        self.shelf_report_button.clicked.connect(lambda: rapor_olustur("raf"))

        ana_layout.addWidget(self.product_report_button)
        ana_layout.addWidget(self.shelf_report_button)

        self.setLayout(ana_layout)

    def urun_ara(self):
        barkod = self.search_bar.text()
        if barkod:
            urun = urun_barkod_ile_al(barkod)
            if urun:
                self.search_result_label.setText(f"Ürün Adı: {urun[1]}, Raf No: {urun[5]}, Miktar: {urun[3]}")
            else:
                self.search_result_label.setText("Ürün bulunamadı.")
        else:
            self.search_result_label.setText("Ürün bilgisi buraya gelecek...")

    def urun_yer_degistir_dialog(self):
        barkod = self.search_bar.text()
        if barkod:
            # Yeni raf numarasını almak için kullanıcıdan input
            yeni_raf_numarasi, ok = QInputDialog.getInt(self, "Yeni Raf Numarası", "Raf Numarasını Girin:", min=1, max=14)
            if ok and urun_yer_degistir(barkod, yeni_raf_numarasi):
                QMessageBox.information(self, "Başarılı", "Ürün başarıyla yer değiştirildi.", QMessageBox.Ok)
            else:
                QMessageBox.warning(self, "Hata", "Ürün yer değiştirilirken bir sorun oluştu.", QMessageBox.Ok)
        else:
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir barkod girin.", QMessageBox.Ok)

    def raf_bilgisi_penceresini_ac(self, raf_numarasi):
        def ac():
            pencerem = RafBilgisiPenceresi(raf_numarasi)
            pencerem.exec_()
        return ac

# Uygulama başlatma
app = QApplication(sys.argv)
window = AnaPencere()
window.show()
sys.exit(app.exec_())
