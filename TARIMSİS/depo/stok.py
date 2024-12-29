import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMenu, QAction, QMessageBox, QInputDialog, QFileDialog, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ProductManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürün Yönetimi")
        self.setGeometry(50, 50, 1000, 700)  # Daha geniş pencere

        # Arayüz teması
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1f1f1f;
                color: white;
            }
            QLabel {
                font-size: 16px;
                color: #e0e0e0;
            }
            QLineEdit, QPushButton {
                font-size: 16px;
                padding: 10px;
                background-color: #444444;
                border: 2px solid #555555;
                color: #ffffff;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QLineEdit {
                min-width: 300px;
            }
            QTableWidget {
                font-size: 14px;
                background-color: #333333;
                gridline-color: #444444;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            QTableWidgetItem {
                background-color: #333333;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #555555;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QMenu {
                background-color: #444444;
                color: white;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 5px 15px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #555555;
            }
        """)

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Ürün Listesi Tablosu (Sağda)
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Resim gösterilmeyecek, aksiyon sütunu ekledik
        self.table.setHorizontalHeaderLabels(["Ürün Adı", "Barkod", "Miktar", "Giriş Tarihi", "Raf No", "Aksiyon"])
        self.layout.addWidget(self.table, 2)  # Tabloyu sağda daha geniş olarak yerleştiriyoruz

        # Ürün ekleme formu (Solda)
        self.form_layout = QVBoxLayout()
        self.form_layout.setSpacing(20)

        self.name_label = QLabel("Ürün Adı:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Ürün adı girin...")
        self.barcode_label = QLabel("Barkod:")
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Barkod numarasını girin...")
        self.quantity_label = QLabel("Miktar:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Miktar girin...")
        self.entry_date_label = QLabel("Giriş Tarihi:")
        self.entry_date_input = QLineEdit()
        self.entry_date_input.setPlaceholderText("Giriş tarihi (yyyy-aa-gg)...")
        self.shelf_number_label = QLabel("Raf No:")
        self.shelf_number_input = QLineEdit()
        self.shelf_number_input.setPlaceholderText("Raf numarasını girin...")
        
        self.image_button = QPushButton("Ürün Resmi Seç")
        self.image_button.clicked.connect(self.select_image)

        self.add_button = QPushButton("Ürün Ekle")
        self.add_button.setStyleSheet("background-color: #4caf50;")
        self.add_button.clicked.connect(self.add_product)

        # Form alanlarını yerleştir
        self.form_layout.addWidget(self.name_label)
        self.form_layout.addWidget(self.name_input)
        self.form_layout.addWidget(self.barcode_label)
        self.form_layout.addWidget(self.barcode_input)
        self.form_layout.addWidget(self.quantity_label)
        self.form_layout.addWidget(self.quantity_input)
        self.form_layout.addWidget(self.entry_date_label)
        self.form_layout.addWidget(self.entry_date_input)
        self.form_layout.addWidget(self.shelf_number_label)
        self.form_layout.addWidget(self.shelf_number_input)
        self.form_layout.addWidget(self.image_button)
        self.form_layout.addWidget(self.add_button)

        self.layout.addLayout(self.form_layout, 1)  # Formu solda daha dar yerleştiriyoruz

        # Ürünleri yükle
        self.load_products()

    def select_image(self):
        # Resim seçme fonksiyonu
        image_path, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Image Files (*.png *.jpg *.bmp *.jpeg *.gif)")
        if image_path:
            self.selected_image_path = image_path

    def add_product(self):
        # Ürün ekleme ve duplicate kontrolü
        name = self.name_input.text()
        barcode = self.barcode_input.text()
        quantity = self.quantity_input.text()
        entry_date = self.entry_date_input.text()
        shelf_number = self.shelf_number_input.text()

        if not all([name, barcode, quantity, entry_date, shelf_number]):
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")
            return

        # Sayısal değerlerin doğru girildiğinden emin olalım
        try:
            quantity = int(quantity)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Miktar sayısal bir değer olmalıdır!")
            return

        # Duplicate kontrolü
        conn = sqlite3.connect(r"C:\Users\Süleyman AKBULUT\Music\TARIMSİS\veritabanları\inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE barcode=?", (barcode,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Hata", "Bu barkodla zaten bir ürün var!")
            conn.close()
            return

        # Resim yolunu kontrol et
        image_path = getattr(self, 'selected_image_path', '')

        cursor.execute("""
        INSERT INTO products (name, barcode, quantity, entry_date, shelf_number, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, barcode, quantity, entry_date, shelf_number, image_path))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi!")
        self.clear_inputs()
        self.load_products()

    def load_products(self):
        # Ürünleri yükle
        self.table.setRowCount(0)
        conn = sqlite3.connect(r"veritabanları\inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, barcode, quantity, entry_date, shelf_number, image_path FROM products")
        products = cursor.fetchall()
        conn.close()

        for row_number, row_data in enumerate(products):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data[1:-1]):  # Resim sütunu hariç veriler
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

            # Aksiyon butonları ekleme
            action_button = QPushButton("Aksiyon")
            action_button.clicked.connect(lambda _, row=row_number: self.show_product_menu(row))
            self.table.setCellWidget(row_number, 5, action_button)

    def clear_inputs(self):
        # Girdi alanlarını temizle
        self.name_input.clear()
        self.barcode_input.clear()
        self.quantity_input.clear()
        self.entry_date_input.clear()
        self.shelf_number_input.clear()

    def show_product_menu(self, row_number):
        menu = QMenu(self)

        # Sağ tık menüsü
        edit_action = QAction("Stok Değiştir", self)
        delete_action = QAction("Ürün Sil", self)
        image_action = QAction("Resmi Görüntüle", self)

        menu.addAction(edit_action)
        menu.addAction(delete_action)
        menu.addAction(image_action)

        edit_action.triggered.connect(lambda: self.edit_stock(row_number))
        delete_action.triggered.connect(lambda: self.delete_product(row_number))
        image_action.triggered.connect(lambda: self.view_image(row_number))

        menu.exec_(self.table.mapToGlobal(self.table.viewport().rect().topLeft()))

    def edit_stock(self, row_number):
        # Stok değiştir
        new_quantity, ok = QInputDialog.getInt(self, "Stok Değiştir", "Yeni miktar:", 1, 0, 10000, 1)
        if ok:
            conn = sqlite3.connect(r"veritabanları\inventory.db")
            cursor = conn.cursor()
            product_id = self.get_product_id_from_row(row_number)
            cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))
            conn.commit()
            conn.close()
            self.load_products()

    def delete_product(self, row_number):
        # Ürün sil
        reply = QMessageBox.question(self, "Ürün Sil", "Bu ürünü silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(r"veritabanları\inventory.db")
            cursor = conn.cursor()
            product_id = self.get_product_id_from_row(row_number)
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            conn.commit()
            conn.close()
            self.load_products()

    def view_image(self, row_number):
        # Ürün resmini görüntüleme
        product_id = self.get_product_id_from_row(row_number)
        conn = sqlite3.connect(r"veritabanları\inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT image_path FROM products WHERE id=?", (product_id,))
        image_path = cursor.fetchone()[0]
        conn.close()

        if image_path:
            pixmap = QPixmap(image_path)
            image_window = QWidget(self)
            image_window.setWindowTitle("Ürün Resmi")
            layout = QVBoxLayout()
            label = QLabel()
            label.setPixmap(pixmap.scaled(500, 500, Qt.KeepAspectRatio))
            layout.addWidget(label)
            close_button = QPushButton("Kapat")
            close_button.clicked.connect(image_window.close)
            layout.addWidget(close_button)
            image_window.setLayout(layout)
            image_window.setGeometry(100, 100, 600, 600)
            image_window.show()

    def get_product_id_from_row(self, row_number):
        # Satır numarasından ürün ID'sini al
        item = self.table.item(row_number, 1)  # Barkod
        barcode = item.text()
        conn = sqlite3.connect(r"veritabanları\inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM products WHERE barcode=?", (barcode,))
        product_id = cursor.fetchone()[0]
        conn.close()
        return product_id


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProductManagementApp()
    window.show()
    sys.exit(app.exec_())
