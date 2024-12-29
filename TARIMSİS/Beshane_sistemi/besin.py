import sqlite3
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt

class Database:
    def __init__(self, db_name="veritabanları\yem_besleme.db"):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_tables()
    


    def yem_ekle(self, yem_adi, miktar_kg, fiyat, silo):
        try:
            self.c.execute("""
                INSERT INTO yem (yem_adi, miktar_kg, fiyat, silo) 
                VALUES (?, ?, ?, ?)""", 
                (yem_adi, miktar_kg, fiyat, silo))
            
            yem_id = self.c.lastrowid
            self.stok_hareketi_ekle(yem_id, "GİRİŞ", miktar_kg, "İlk stok girişi")
            
            self.conn.commit()
            return True, f"{yem_adi} başarıyla eklendi."
        except sqlite3.Error as e:
            return False, f"Hata: {e}"

    def yemleri_listele(self):
        try:
            self.c.execute("""
                SELECT y.*, 
                    (SELECT COUNT(*) FROM stok_hareketleri WHERE yem_id = y.id) as hareket_sayisi
                FROM yem y
                ORDER BY y.son_guncelleme DESC
            """)
            return True, self.c.fetchall()
        except sqlite3.Error as e:
            return False, f"Hata: {e}"

    def stok_hareketi_ekle(self, yem_id, hareket_tipi, miktar, aciklama=""):
        try:
            self.c.execute("""
                INSERT INTO stok_hareketleri (yem_id, hareket_tipi, miktar, aciklama)
                VALUES (?, ?, ?, ?)
            """, (yem_id, hareket_tipi, miktar, aciklama))
            
            # Stok miktarını güncelle
            if hareket_tipi == "GİRİŞ":
                self.c.execute("""
                    UPDATE yem 
                    SET miktar_kg = miktar_kg + ?,
                        son_guncelleme = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (miktar, yem_id))
            else:
                self.c.execute("""
                    UPDATE yem 
                    SET miktar_kg = miktar_kg - ?,
                        son_guncelleme = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (miktar, yem_id))
            
            self.conn.commit()
            return True, "Stok hareketi başarıyla kaydedildi."
        except sqlite3.Error as e:
            return False, f"Hata: {e}"

    def __del__(self):
        self.conn.close()

class StokHareketiDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, yem_id=None):
        super().__init__(parent)
        self.yem_id = yem_id
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Stok Hareketi Ekle")
        layout = QtWidgets.QVBoxLayout()
        
        # Hareket tipi
        self.hareket_tipi = QtWidgets.QComboBox()
        self.hareket_tipi.addItems(["GİRİŞ", "ÇIKIŞ"])
        layout.addWidget(QtWidgets.QLabel("Hareket Tipi:"))
        layout.addWidget(self.hareket_tipi)
        
        # Miktar
        self.miktar = QtWidgets.QLineEdit()
        self.miktar.setValidator(QtGui.QDoubleValidator())
        layout.addWidget(QtWidgets.QLabel("Miktar (kg):"))
        layout.addWidget(self.miktar)
        
        # Açıklama
        self.aciklama = QtWidgets.QTextEdit()
        layout.addWidget(QtWidgets.QLabel("Açıklama:"))
        layout.addWidget(self.aciklama)
        
        # Butonlar
        buttons = QtWidgets.QHBoxLayout()
        self.btn_kaydet = QtWidgets.QPushButton("Kaydet")
        self.btn_iptal = QtWidgets.QPushButton("İptal")
        buttons.addWidget(self.btn_kaydet)
        buttons.addWidget(self.btn_iptal)
        
        self.btn_kaydet.clicked.connect(self.accept)
        self.btn_iptal.clicked.connect(self.reject)
        
        layout.addLayout(buttons)
        self.setLayout(layout)

class YemEklemeUygulamasi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Yem Takip Sistemi")
        self.setMinimumSize(800, 600)
        
        # Ana widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        layout = QtWidgets.QHBoxLayout(central_widget)
        
        # Sol panel - Yem ekleme formu
        form_group = QtWidgets.QGroupBox("Yem Ekle")
        form_layout = QtWidgets.QFormLayout()
        
        self.input_yem_adi = QtWidgets.QLineEdit()
        self.input_miktar_kg = QtWidgets.QLineEdit()
        self.input_miktar_kg.setValidator(QtGui.QDoubleValidator())
        self.input_fiyat = QtWidgets.QLineEdit()
        self.input_fiyat.setValidator(QtGui.QDoubleValidator())
        self.input_silo = QtWidgets.QLineEdit()
        
        form_layout.addRow("Yem Adı:", self.input_yem_adi)
        form_layout.addRow("Miktar (kg):", self.input_miktar_kg)
        form_layout.addRow("Fiyat (TL):", self.input_fiyat)
        form_layout.addRow("Silo:", self.input_silo)
        
        self.btn_ekle = QtWidgets.QPushButton("Yem Ekle")
        self.btn_ekle.clicked.connect(self.yem_ekle)
        form_layout.addRow(self.btn_ekle)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Sağ panel - Yem listesi
        list_group = QtWidgets.QGroupBox("Yem Listesi")
        list_layout = QtWidgets.QVBoxLayout()
        
        # Tablo
        self.tablo = QtWidgets.QTableWidget()
        self.tablo.setColumnCount(7)
        self.tablo.setHorizontalHeaderLabels([
            "ID", "Yem Adı", "Miktar (kg)", "Fiyat (TL)", 
            "Silo", "Son Güncelleme", "Hareketler"
        ])
        self.tablo.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablo.customContextMenuRequested.connect(self.show_context_menu)
        
        list_layout.addWidget(self.tablo)
        
        # Yenile butonu
        self.btn_yenile = QtWidgets.QPushButton("Listeyi Yenile")
        self.btn_yenile.clicked.connect(self.yemleri_listele)
        list_layout.addWidget(self.btn_yenile)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Durum çubuğu
        self.statusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.yemleri_listele()

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        stok_hareketi_ekle = menu.addAction("Stok Hareketi Ekle")
        
        action = menu.exec_(self.tablo.viewport().mapToGlobal(position))
        
        if action == stok_hareketi_ekle:
            row = self.tablo.currentRow()
            if row >= 0:
                yem_id = int(self.tablo.item(row, 0).text())
                self.stok_hareketi_ekle_dialog(yem_id)

    def stok_hareketi_ekle_dialog(self, yem_id):
        dialog = StokHareketiDialog(self, yem_id)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            hareket_tipi = dialog.hareket_tipi.currentText()
            miktar = float(dialog.miktar.text())
            aciklama = dialog.aciklama.toPlainText()
            
            success, message = self.db.stok_hareketi_ekle(yem_id, hareket_tipi, miktar, aciklama)
            if success:
                self.yemleri_listele()
            self.statusBar.showMessage(message, 3000)

    def yem_ekle(self):
        yem_adi = self.input_yem_adi.text()
        miktar_kg = self.input_miktar_kg.text()
        fiyat = self.input_fiyat.text()
        silo = self.input_silo.text()

        if all([yem_adi, miktar_kg, fiyat, silo]):
            try:
                miktar_kg = float(miktar_kg)
                fiyat = float(fiyat)
                
                success, message = self.db.yem_ekle(yem_adi, miktar_kg, fiyat, silo)
                if success:
                    self.input_yem_adi.clear()
                    self.input_miktar_kg.clear()
                    self.input_fiyat.clear()
                    self.input_silo.clear()
                    self.yemleri_listele()
                
                self.statusBar.showMessage(message, 3000)
            except ValueError:
                self.statusBar.showMessage("Lütfen geçerli sayısal değerler girin.", 3000)
        else:
            self.statusBar.showMessage("Lütfen tüm alanları doldurun.", 3000)

    def yemleri_listele(self):
        success, kayitlar = self.db.yemleri_listele()
        
        if success:
            self.tablo.setRowCount(len(kayitlar))
            for row, kayit in enumerate(kayitlar):
                for col, veri in enumerate(kayit):
                    if col < 7:  # Son sütun hareket sayısı
                        if col == 5:  # Tarih sütunu
                            veri = datetime.strptime(veri, '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
                        item = QtWidgets.QTableWidgetItem(str(veri))
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Düzenlemeyi engelle
                        self.tablo.setItem(row, col, item)
            
            self.tablo.resizeColumnsToContents()
        else:
            self.statusBar.showMessage(kayitlar, 3000)  # kayitlar burada hata mesajı içeriyor

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    
    # Stil ayarları
    app.setStyle('Fusion')
    
    # Koyu tema
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, Qt.white)
    palette.setColor(QtGui.QPalette.Text, Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    palette.setColor(QtGui.QPalette.HighlightedText, Qt.black)
    
    app.setPalette(palette)
    
    pencere = YemEklemeUygulamasi()
    pencere.show()
    app.exec_()