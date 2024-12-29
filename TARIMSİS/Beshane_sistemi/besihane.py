import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox, QStackedWidget, QGridLayout, QInputDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class AnimalManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Besihane Yönetim Sistemi")
        self.setGeometry(100, 100, 1200, 800)

        self.beshane_count = 14
        self.initUI()
        self.createDatabase()
        self.setStyleSheet(self.loadStyle())

    def initUI(self):
        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Hayvan Küupe No Ara...")
        self.search_bar.textChanged.connect(self.searchAnimal)
        search_layout.addWidget(self.search_bar)

        self.beshane_grid = QGridLayout()
        self.beshane_cards = []
        for i in range(self.beshane_count):
            card = QPushButton(f"Besihane {i + 1}")
            card.setObjectName(f"beshane_{i + 1}")
            card.clicked.connect(self.showBeshaneAnimals)
            self.beshane_grid.addWidget(card, i // 4, i % 4)
            self.beshane_cards.append(card)

        self.animal_table = QTableWidget()
        self.animal_table.setColumnCount(5)
        self.animal_table.setHorizontalHeaderLabels(["Küupe No", "Doğum Yılı", "Cinsi", "Besihane", "Sigorta"])
        self.animal_table.setAlternatingRowColors(True)
        self.animal_table.setSelectionBehavior(QTableWidget.SelectRows)

        self.change_beshane_button = QPushButton("Hayvanın Yerini Değiştir")
        self.change_beshane_button.clicked.connect(self.changeAnimalLocation)

        self.back_button = QPushButton("Geri")
        self.back_button.clicked.connect(self.goBackToHome)

        self.stacked_widget = QStackedWidget()

        home_widget = QWidget()
        home_layout = QVBoxLayout()
        home_layout.addLayout(search_layout)
        home_layout.addLayout(self.beshane_grid)
        home_widget.setLayout(home_layout)

        beshane_widget = QWidget()
        beshane_layout = QVBoxLayout()
        beshane_layout.addWidget(self.animal_table)
        beshane_layout.addWidget(self.change_beshane_button)
        beshane_layout.addWidget(self.back_button)
        beshane_widget.setLayout(beshane_layout)

        self.stacked_widget.addWidget(home_widget)
        self.stacked_widget.addWidget(beshane_widget)

        layout.addWidget(self.stacked_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def createDatabase(self):
        self.conn = sqlite3.connect("hayvanlar.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS hayvanlar (
                kupeno TEXT PRIMARY KEY,
                dogumyili INTEGER,
                cins TEXT,
                beshane INTEGER,
                sigorta TEXT
            )
        """
        )
        self.conn.commit()
        self.loadAnimals()

    def loadAnimals(self):
        self.cursor.execute("SELECT * FROM hayvanlar")
        self.animals = self.cursor.fetchall()

    def searchAnimal(self):
        search_text = self.search_bar.text()
        if not search_text:
            return

        self.cursor.execute("SELECT beshane FROM hayvanlar WHERE kupeno = ?", (search_text,))
        result = self.cursor.fetchone()
        if result:
            QMessageBox.information(self, "Sonuç", f"Hayvan Besihane {result[0]} içinde bulunuyor.")
        else:
            QMessageBox.warning(self, "Sonuç", "Hayvan bulunamadı!")

    def showBeshaneAnimals(self):
        sender = self.sender()
        beshane_no = int(sender.objectName().split('_')[1])

        self.cursor.execute("SELECT * FROM hayvanlar WHERE beshane = ?", (beshane_no,))
        rows = self.cursor.fetchall()

        self.animal_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.animal_table.setItem(i, j, QTableWidgetItem(str(value)))

        self.stacked_widget.setCurrentIndex(1)

    def changeAnimalLocation(self):
        selected_row = self.animal_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Hata", "Lütfen bir hayvan seçin!")
            return

        kupeno = self.animal_table.item(selected_row, 0).text()
        new_beshane, ok = QInputDialog.getText(self, "Besihane Değiştir", "Yeni besihane numarasını girin:")

        if ok and new_beshane.isdigit():
            self.cursor.execute("UPDATE hayvanlar SET beshane = ? WHERE kupeno = ?", (int(new_beshane), kupeno))
            self.conn.commit()
            QMessageBox.information(self, "Başarılı", "Hayvanın besihane yeri güncellendi!")
            self.showBeshaneAnimals()
        else:
            QMessageBox.warning(self, "Hata", "Geçerli bir besihane numarası giriniz!")

    def goBackToHome(self):
        self.stacked_widget.setCurrentIndex(0)

    def loadStyle(self):
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
        QLineEdit {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border: none;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QTableWidget {
            background-color: white;
            border: 1px solid #ccc;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            font-weight: bold;
        }
        """

    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnimalManagementSystem()
    window.show()
    sys.exit(app.exec_())
