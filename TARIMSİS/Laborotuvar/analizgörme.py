import sys
import sqlite3
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DatabaseViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Veritabanı Görüntüleyici")
        self.setGeometry(100, 100, 1000, 600)
        
        self.layout = QVBoxLayout()

        # Buttons
        self.sut_button = QPushButton("Süt Analizleri")
        self.meyve_button = QPushButton("Meyve Analizleri")
        self.et_button = QPushButton("Et Analizleri")
        self.hayvan_button = QPushButton("Hayvan Analizleri")
        
        # Connect buttons to functions
        self.sut_button.clicked.connect(self.show_sut_data)
        self.meyve_button.clicked.connect(self.show_meyve_data)
        self.et_button.clicked.connect(self.show_et_data)
        self.hayvan_button.clicked.connect(self.show_hayvan_data)
        
        # Horizontal layout for buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.sut_button)
        self.button_layout.addWidget(self.meyve_button)
        self.button_layout.addWidget(self.et_button)
        self.button_layout.addWidget(self.hayvan_button)
        
        # Add table
        self.table = QTableWidget()
        self.table.setFont(QFont('Arial', 12))
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        # Set a modern style using QSS
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #008CBA;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005f6b;
            }
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #dcdcdc;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #d3d3d3;
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
                border: none;
            }
        """)

    def show_data(self, db_path, table_name):
        if not os.path.exists(db_path):
            QMessageBox.critical(self, "Hata", f"Veritabanı bulunamadı: {db_path}")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]

            # Update the table
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)

            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table.setItem(row_idx, col_idx, item)
            
            self.table.resizeColumnsToContents()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Veritabanı Hatası", f"Veritabanı hatası: {e}")
        finally:
            conn.close()
    
    def show_sut_data(self):
        self.show_data(r'veritabanları\sut_laboratuvar.db', 'sut_analizleri')
    
    def show_meyve_data(self):
        self.show_data(r'veritabanları\meyve_sebze_laboratuvar.db', 'analizler')
    
    def show_et_data(self):
        self.show_data(r'veritabanları\et_laboratuvar.db', 'et_analizleri')
    
    def show_hayvan_data(self):
        self.show_data(r'veritabanları\hayvanlar_laboratuvar.db', 'analizler')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DatabaseViewer()
    window.show()
    sys.exit(app.exec_())