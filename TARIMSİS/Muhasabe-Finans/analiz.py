import sys
import sqlite3
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QFileDialog, QHBoxLayout, QGroupBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.linear_model import LinearRegression

# SQLite bağlantısı
conn = sqlite3.connect(r'veritabanları\inventory.db')
cursor = conn.cursor()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BEDROCK TEAM STOK VE SATIŞ GRAFİK SİSTEMİ")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #1E1E1E;")

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # Başlık
        self.header_label = QLabel("BEDROCK TEAM STOK VE SATIŞ GRAFİK SİSTEMİ", self)
        self.header_label.setFont(QFont("Orbitron", 24, QFont.Bold))
        self.header_label.setStyleSheet("color: #00FFC6;")
        self.header_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.header_label)

        # Button layout (Horizontal)
        self.button_layout = QHBoxLayout()

        # Buttons
        self.btn_bar_chart = self.create_button("Ürün Stok Miktarları", self.show_bar_chart)
        self.btn_line_chart = self.create_button("Satış Miktarı Zamanla", self.show_line_chart)
        self.btn_pie_chart = self.create_button("Şirketlere Göre Satış Dağılımı", self.show_pie_chart)
        self.btn_sales_bar_chart = self.create_button("Ürünlere Göre Satış Miktarı", self.show_sales_bar_chart)
        self.btn_predict_sales = self.create_button("Satış Tahmini Yap", self.predict_sales)
        self.btn_export_excel = self.create_button("Excel'e Aktar", self.export_to_excel)

        # Adding buttons to the layout
        self.button_layout.addWidget(self.btn_bar_chart)
        self.button_layout.addWidget(self.btn_line_chart)
        self.button_layout.addWidget(self.btn_pie_chart)
        self.button_layout.addWidget(self.btn_sales_bar_chart)
        self.button_layout.addWidget(self.btn_predict_sales)
        self.button_layout.addWidget(self.btn_export_excel)
        
        # Group Box for buttons to make them more organized
        button_group = QGroupBox()
        button_group.setStyleSheet("background-color: #333333; border-radius: 10px;")
        button_group.setLayout(self.button_layout)

        self.layout.addWidget(button_group)

        # Prediction label
        self.prediction_label = QLabel("Satış Tahmini: Henüz tahmin yapılmadı", self)
        self.prediction_label.setFont(QFont("Orbitron", 14))
        self.prediction_label.setStyleSheet("color: #00FFC6;")
        self.prediction_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.prediction_label)

        # Canvas area for displaying graphs
        self.canvas_widget = QWidget(self)
        self.canvas_layout = QVBoxLayout(self.canvas_widget)
        self.layout.addWidget(self.canvas_widget)

    def create_button(self, text, callback):
        button = QPushButton(text, self)
        button.setFont(QFont("Orbitron", 12))
        button.setStyleSheet("background-color: #00A3FF; color: white; border: none; padding: 10px; border-radius: 5px;")
        button.clicked.connect(callback)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedWidth(180)
        return button

    def show_line_chart(self):
        self.clear_canvas()
        cursor.execute("SELECT sale_date, quantity FROM sales")
        sales = cursor.fetchall()
        dates = [sale[0] for sale in sales]
        quantities = [sale[1] for sale in sales]

        fig, ax = plt.subplots()
        ax.plot(dates, quantities, marker='o', linestyle='-', color='#00FFC6')
        ax.set_xlabel('Tarih', color='#00FFC6')
        ax.set_ylabel('Satış Miktarı', color='#00FFC6')
        ax.set_title('Satış Miktarı Zamanla', color='#00FFC6')
        plt.xticks(rotation=45, color='#00FFC6')
        plt.yticks(color='#00FFC6')
        fig.patch.set_facecolor('#1E1E1E')
        ax.set_facecolor('#2A2A2A')
        self.display_canvas(fig)

    def show_pie_chart(self):
        self.clear_canvas()
        cursor.execute("SELECT company_name, SUM(quantity) FROM sales GROUP BY company_name")
        sales_by_company = cursor.fetchall()
        companies = [sale[0] for sale in sales_by_company]
        quantities = [sale[1] for sale in sales_by_company]

        fig, ax = plt.subplots()
        ax.pie(quantities, labels=companies, autopct='%1.1f%%', startangle=90, colors=['#00FFC6', '#00A3FF', '#FF00C6', '#FFC600'])
        ax.set_title('Şirketlere Göre Satış Dağılımı', color='#00FFC6')
        fig.patch.set_facecolor('#1E1E1E')
        ax.set_facecolor('#2A2A2A')
        self.display_canvas(fig)

    def show_bar_chart(self):
        self.clear_canvas()
        cursor.execute("SELECT name, quantity FROM products")
        products = cursor.fetchall()
        names = [product[0] for product in products]
        quantities = [product[1] for product in products]

        fig, ax = plt.subplots()
        ax.bar(names, quantities, color='#00FFC6')
        ax.set_xlabel('Ürün Adı', color='#00FFC6')
        ax.set_ylabel('Miktar', color='#00FFC6')
        ax.set_title('Ürün Stok Miktarları', color='#00FFC6')
        plt.xticks(rotation=90, color='#00FFC6')
        plt.yticks(color='#00FFC6')
        fig.patch.set_facecolor('#1E1E1E')
        ax.set_facecolor('#2A2A2A')
        self.display_canvas(fig)

    def show_sales_bar_chart(self):
        self.clear_canvas()
        cursor.execute("SELECT p.name, SUM(s.quantity) FROM sales s JOIN products p ON s.barcode = p.barcode GROUP BY p.name")
        sales = cursor.fetchall()
        product_names = [sale[0] for sale in sales]
        quantities = [sale[1] for sale in sales]

        fig, ax = plt.subplots()
        ax.bar(product_names, quantities, color='#00FFC6')
        ax.set_xlabel('Ürün Adı', color='#00FFC6')
        ax.set_ylabel('Satış Miktarı', color='#00FFC6')
        ax.set_title('Ürünlere Göre Satış Miktarı', color='#00FFC6')
        plt.xticks(rotation=90, color='#00FFC6')
        plt.yticks(color='#00FFC6')
        fig.patch.set_facecolor('#1E1E1E')
        ax.set_facecolor('#2A2A2A')
        self.display_canvas(fig)

    def predict_sales(self):
        cursor.execute("SELECT quantity, sale_date FROM sales")
        sales_data = cursor.fetchall()
        if not sales_data:
            return
        dates = [sale[1] for sale in sales_data]
        quantities = [sale[0] for sale in sales_data]
        x = np.array(range(len(dates))).reshape(-1, 1)
        y = np.array(quantities)
        model = LinearRegression()
        model.fit(x, y)
        predicted_sales = model.predict(np.array([[len(dates) + 30]]))
        self.prediction_label.setText(f"Satış Tahmini: {predicted_sales[0]:.2f} ürün")

    def export_to_excel(self):
        cursor.execute("SELECT name, quantity FROM products")
        products = cursor.fetchall()
        df = pd.DataFrame(products, columns=['Ürün Adı', 'Stok Miktarı'])
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Excel'e Aktar", "", "Excel Files (*.xlsx)", options=options)
        if file_path:
            df.to_excel(file_path, index=False)
            QMessageBox.information(self, "Excel'e Aktarma", "Veriler başarıyla aktarıldı")

    def display_canvas(self, fig):
        canvas = FigureCanvas(fig)
        self.canvas_layout.addWidget(canvas)
        canvas.draw()

    def clear_canvas(self):
        for i in reversed(range(self.canvas_layout.count())):
            widget = self.canvas_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
