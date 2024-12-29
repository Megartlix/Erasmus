import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import QDate

class RevenueApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Gelir Hesaplama Uygulaması')
        self.setGeometry(100, 100, 600, 350)

        self.revenue_label = QLabel('Toplam Gelir: 0 TL', self)

        self.calculate_button = QPushButton('Geliri Kaydet', self)
        self.calculate_button.clicked.connect(self.calculate_revenue)

        layout = QVBoxLayout()
        layout.addWidget(self.revenue_label)
        layout.addWidget(self.calculate_button)
        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #F5F5F5;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 15px 32px;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin-top: 20px;
            }
        """)

        self.update_revenue_display()

    def calculate_revenue(self):
        try:
            conn_inventory = sqlite3.connect(r'veritabanları/inventory.db')
            cursor_inventory = conn_inventory.cursor()

            conn_sales = sqlite3.connect(r'veritabanları/satış.db')
            cursor_sales = conn_sales.cursor()

            sales_query = """
                SELECT price, total_price FROM sales
            """
            cursor_inventory.execute(sales_query)
            sales_data = cursor_inventory.fetchall()

            total_revenue = 0

            for sale in sales_data:
                total_revenue += sale[0] * sale[1]

            self.revenue_label.setText(f'Toplam Gelir: {total_revenue:.2f} TL')

            self.save_revenue(total_revenue)

            conn_inventory.close()
            conn_sales.close()

            self.show_message('Başarılı', 'Gelir başarıyla kaydedildi.')

        except sqlite3.Error as e:
            self.show_message('Hata', f'Bir hata oluştu: {e}')

    def save_revenue(self, revenue):
        try:
            conn_revenue = sqlite3.connect(r'veritabanları/gelirler.db')
            cursor_revenue = conn_revenue.cursor()

            current_date = QDate.currentDate().toString('yyyy-MM-dd')
            insert_query = """
                INSERT INTO gelirler (gelir, tarih) VALUES (?, ?)
            """
            cursor_revenue.execute(insert_query, (revenue, current_date))
            conn_revenue.commit()

            conn_revenue.close()

            self.update_revenue_display()

        except sqlite3.Error as e:
            self.show_message('Hata', f'Gelir kaydedilirken bir hata oluştu: {e}')

    def update_revenue_display(self):
     try:
        conn_revenue = sqlite3.connect(r'veritabanları/gelirler.db')
        cursor_revenue = conn_revenue.cursor()

        select_query = """
            SELECT gelir FROM gelirler ORDER BY tarih DESC LIMIT 1
        """
        cursor_revenue.execute(select_query)
        revenue_data = cursor_revenue.fetchone()

        if revenue_data and revenue_data[0]:  # Verinin varlığını ve boş olmadığını kontrol et
            try:
                # Değer float'a dönüştürülebilir mi kontrol edin
                revenue_float = float(revenue_data[0])
                self.revenue_label.setText(f'Toplam Gelir: {revenue_float:.2f} TL')
            except ValueError:
                # Eğer dönüştürülemezse varsayılan bir değer göster
                self.revenue_label.setText('Toplam Gelir: 0 TL')
        else:
            self.revenue_label.setText('Toplam Gelir: 0 TL')

        conn_revenue.close()

     except sqlite3.Error as e:
        self.show_message('Hata', f'Gelir verisi alınırken bir hata oluştu: {e}')

       

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RevenueApp()
    window.show()
    sys.exit(app.exec_())