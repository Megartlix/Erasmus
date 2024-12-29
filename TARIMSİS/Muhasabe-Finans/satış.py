import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime

class SalesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satış Yönetimi")
        self.setGeometry(100, 100, 1000, 700)

        self.setStyleSheet(""" 
            QMainWindow {
                background-color: #2c2f38;
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
        """)

        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Satış Formu
        self.name_label = QLabel("Firma Adı:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Firma adı girin...")

        self.barcode_label = QLabel("Barkod:")
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Barkod numarasını girin...")

        self.quantity_label = QLabel("Miktar:")
        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Satış miktarını girin...")

        self.price_label = QLabel("Fiyat:")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Ürün fiyatını girin...")

        self.vat_label = QLabel("KDV Oranı (%):")
        self.vat_input = QLineEdit()
        self.vat_input.setPlaceholderText("KDV oranını girin...")

        self.discount_label = QLabel("İskonto Oranı (%):")
        self.discount_input = QLineEdit()
        self.discount_input.setPlaceholderText("İskonto oranını girin...")

        self.add_product_button = QPushButton("Ürün Ekle")
        self.add_product_button.clicked.connect(self.add_product)

        self.sale_button = QPushButton("Satışı Gerçekleştir")
        self.sale_button.clicked.connect(self.make_sale)

        self.invoice_button = QPushButton("Fatura Oluştur")
        self.invoice_button.clicked.connect(self.generate_invoice)

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.barcode_label)
        self.layout.addWidget(self.barcode_input)
        self.layout.addWidget(self.quantity_label)
        self.layout.addWidget(self.quantity_input)
        self.layout.addWidget(self.price_label)
        self.layout.addWidget(self.price_input)
        self.layout.addWidget(self.vat_label)
        self.layout.addWidget(self.vat_input)
        self.layout.addWidget(self.discount_label)
        self.layout.addWidget(self.discount_input)
        self.layout.addWidget(self.add_product_button)
        self.layout.addWidget(self.sale_button)
        self.layout.addWidget(self.invoice_button)

        self.products = []
        self.load_sales()

    def add_product(self):
        barcode = self.barcode_input.text()
        quantity = self.quantity_input.text()
        price = self.price_input.text()
        vat = self.vat_input.text()
        discount = self.discount_input.text()

        # Girdi kontrolü
        if not barcode or not quantity or not price or not vat or not discount:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        try:
            quantity = int(quantity)
            price = float(price)
            vat = float(vat)
            discount = float(discount)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Miktar, fiyat, KDV ve iskonto geçerli bir sayı olmalıdır.")
            return

        self.products.append({
            "barcode": barcode,
            "quantity": quantity,
            "price": price,
            "vat": vat,
            "discount": discount
        })

        QMessageBox.information(self, "Başarılı", "Ürün başarıyla eklendi!")
        self.barcode_input.clear()
        self.quantity_input.clear()
        self.price_input.clear()
        self.vat_input.clear()
        self.discount_input.clear()

    def make_sale(self):
        company_name = self.name_input.text()

        # Girdi kontrolü
        if not company_name or not self.products:
            QMessageBox.warning(self, "Hata", "Lütfen firma adını ve en az bir ürün girin.")
            return

        conn = sqlite3.connect(r"veritabanları/inventory.db")
        cursor = conn.cursor()

        total_price = 0
        for product in self.products:
            barcode = product["barcode"]
            quantity = product["quantity"]
            price = product["price"]
            vat = product["vat"]
            discount = product["discount"]

            # İskonto ve KDV hesaplama
            discounted_price = price * (1 - discount / 100)
            total_price_without_vat = discounted_price * quantity
            total_vat = total_price_without_vat * (vat / 100)
            product_total_price = total_price_without_vat + total_vat

            cursor.execute("SELECT quantity FROM products WHERE barcode=?", (barcode,))
            product_data = cursor.fetchone()

            if not product_data:
                QMessageBox.warning(self, "Hata", f"{barcode} barkoduyla kayıtlı ürün bulunamadı.")
                conn.close()
                return

            stock_quantity = product_data[0]
            if stock_quantity < quantity:
                QMessageBox.warning(self, "Hata", f"{barcode} barkoduyla yeterli stok yok!")
                conn.close()
                return

            cursor.execute("""
                INSERT INTO sales (barcode, quantity, company_name, price, total_price, sale_date)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (barcode, quantity, company_name, discounted_price, product_total_price))
            conn.commit()

            # Ürün stoğunu güncelleme
            new_quantity = stock_quantity - quantity
            cursor.execute("UPDATE products SET quantity=? WHERE barcode=?", (new_quantity, barcode))
            conn.commit()

            total_price += product_total_price

        QMessageBox.information(self, "Başarılı", f"{company_name} için satış başarıyla gerçekleştirildi! Toplam Tutar: {total_price:.2f} TL")
        self.name_input.clear()
        self.products = []
        conn.close()
        self.load_sales()

    def generate_invoice(self):
        company_name = self.name_input.text()

        if not company_name or not self.products:
            QMessageBox.warning(self, "Hata", "Lütfen firma adını ve en az bir ürün girin.")
            return

        # Fatura dosyasının kaydedileceği yolu seçmek
        file_dialog = QFileDialog(self)
        file_dialog.setDefaultSuffix(".pdf")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_path, _ = file_dialog.getSaveFileName(self, "Faturayı Kaydet", "", "PDF Files (*.pdf)")

        if not file_path:
            return  # Kullanıcı dosya kaydetmeyi iptal etti.

        # PDF oluşturma
        c = canvas.Canvas(file_path, pagesize=letter)
        c.setFont("Helvetica", 12)

        # Şirket logosu ve e-fatura logosu ekleme (logoları sağladığınız dosyalarla değiştirebilirsiniz)
        c.drawImage(r"resimler\12122.png", 50, 720, width=70, height=70, mask='auto')
        c.drawImage(r"resimler\vergi.png", 470, 720, width=70, height=70, mask='auto')  # Logo sağ üst

        # Sabit vergi bilgileri
        c.drawString(50, 730, "Vergı Dairesı: Hasan Tahsin Vergi Dairesi")
        c.drawString(50, 710, "Vergı Numarası: 132U9434734")

        # Fatura detaylarını ekleme
        c.drawString(50, 690, f"Fırma Adı: {company_name}")

        # Tablo oluşturma
        data = [["Barkod", "Mıktar", "Fıyat", "KDV Oranı", "ıskonto Oranı", "Toplam Tutar"]]
        total_price_without_vat = 0
        total_vat = 0
        total_discount = 0
        total_price = 0

        for product in self.products:
            barcode = product["barcode"]
            quantity = product["quantity"]
            price = product["price"]
            vat = product["vat"]
            discount = product["discount"]

            discounted_price = price * (1 - discount / 100)
            item_total_price_without_vat = discounted_price * quantity
            item_total_vat = item_total_price_without_vat * (vat / 100)
            item_total_price = item_total_price_without_vat + item_total_vat

            data.append([barcode, quantity, f"{price:.2f} TL", f"{vat:.2f}%", f"{discount:.2f}%", f"{item_total_price:.2f} TL"])

            total_price_without_vat += item_total_price_without_vat
            total_vat += item_total_vat
            total_discount += (price * discount / 100) * quantity
            total_price += item_total_price

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        table_width, table_height = table.wrapOn(c, 400, 600)
        table.drawOn(c, 50, 600 - table_height)

        y_position = 600 - table_height - 30

        # Toplam fiyat, iskonto ve KDV bilgilerini ekleme
        c.drawString(50, y_position, f"Toplam Fiyat (ıskonto ve KDV Harıç): {total_price_without_vat:.2f} TL")
        c.drawString(50, y_position - 20, f"Toplam ıskonto: {total_discount:.2f} TL")
        c.drawString(50, y_position - 40, f"Toplam KDV: {total_vat:.2f} TL")
        c.drawString(50, y_position - 60, f"Toplam Fıyat: {total_price:.2f} TL")

        # İmza Alanı
        c.line(50, 120, 200, 120)  # İmza çizgisi
        c.drawString(50, 100, "ımza:")

        # Fatura tarihi
        c.drawString(400, 100, f"Fatura Tarıhı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()

        QMessageBox.information(self, "Başarılı", f"Fatura başarıyla oluşturuldu: {file_path}")

    def load_sales(self):
        # Satışları görüntüleme
        conn = sqlite3.connect(r"veritabanları/inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT barcode, quantity, company_name, price, total_price, sale_date FROM sales")
        sales = cursor.fetchall()
        conn.close()

        # Satış tablosunu güncelleme
        if hasattr(self, 'sales_table'):
            self.sales_table.setRowCount(0)
        else:
            self.sales_table = QTableWidget(self)
            self.sales_table.setColumnCount(6)
            self.sales_table.setHorizontalHeaderLabels([
                "Barkod", "Mıktar", "Fırma Adı", "Birim Fıyat", "Toplam Tutar", "Satıs Tarıhı"
            ])
            self.layout.addWidget(self.sales_table)

        for row_number, row_data in enumerate(sales):
            self.sales_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.sales_table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesApp()
    window.show()
    sys.exit(app.exec_())