import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QWidget, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class AnimalManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hayvan Ekleme Sistemi - Modern Tasarım")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()
        self.createDatabase()
        self.setStyleSheet(self.loadStyle())

    def initUI(self):
        # Ana layout
        layout = QVBoxLayout()

        # Form alanı
        form_layout = QHBoxLayout()

        form_left = QVBoxLayout()
        form_right = QVBoxLayout()

        self.label_kupeno = QLabel("Hayvan Küpe No:")
        self.input_kupeno = QLineEdit()
        self.label_dogumyili = QLabel("Doğum Yılı:")
        self.input_dogumyili = QLineEdit()
        self.label_cins = QLabel("Hayvan Cinsi:")
        self.input_cins = QLineEdit()
        self.label_beshane = QLabel("Bulunduğu Besihane:")
        self.input_beshane = QLineEdit()
        self.label_sigorta = QLabel("Sigorta Var mı?")
        self.input_sigorta = QCheckBox("Evet")

        # Font ayarları
        for label in [self.label_kupeno, self.label_dogumyili, self.label_cins, self.label_beshane, self.label_sigorta]:
            label.setFont(QFont("Arial", 12, QFont.Bold))

        # Form alanını sol tarafa yerleştir
        form_left.addWidget(self.label_kupeno)
        form_left.addWidget(self.input_kupeno)
        form_left.addWidget(self.label_dogumyili)
        form_left.addWidget(self.input_dogumyili)

        # Form alanını sağ tarafa yerleştir
        form_right.addWidget(self.label_cins)
        form_right.addWidget(self.input_cins)
        form_right.addWidget(self.label_beshane)
        form_right.addWidget(self.input_beshane)
        form_right.addWidget(self.label_sigorta)
        form_right.addWidget(self.input_sigorta)

        form_layout.addLayout(form_left)
        form_layout.addLayout(form_right)

        # Butonlar
        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.addAnimal)
        self.add_button.setObjectName("add_button")

        # Tablo
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Küpe No", "Doğum Yılı", "Cinsi", "Besihane", "Sigorta"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)

        # Tüm widgetleri ana layouta ekle
        layout.addLayout(form_layout)
        layout.addWidget(self.add_button)
        layout.addWidget(self.table)

        # Merkezi widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def createDatabase(self):
        self.conn = sqlite3.connect("veritabanları\hayvanlar.db")
        self.cursor = self.conn.cursor()
        self.loadAnimals()

    def addAnimal(self):
        kupeno = self.input_kupeno.text()
        dogumyili = self.input_dogumyili.text()
        cins = self.input_cins.text()
        beshane = self.input_beshane.text()
        sigorta = "Evet" if self.input_sigorta.isChecked() else "Hayır"

        if not kupeno or not dogumyili or not cins or not beshane:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return

        try:
            self.cursor.execute("INSERT INTO hayvanlar (kupeno, dogumyili, cins, beshane, sigorta) VALUES (?, ?, ?, ?, ?)",
                                (kupeno, dogumyili, cins, beshane, sigorta))
            self.conn.commit()
            QMessageBox.information(self, "Başarılı", "Hayvan başarıyla eklendi!")
            self.loadAnimals()
            self.clearInputs()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu küpe numarası zaten kayıtlı!")

    def loadAnimals(self):
        self.cursor.execute("SELECT * FROM hayvanlar")
        rows = self.cursor.fetchall()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

    def clearInputs(self):
        self.input_kupeno.clear()
        self.input_dogumyili.clear()
        self.input_cins.clear()
        self.input_beshane.clear()
        self.input_sigorta.setChecked(False)

    def loadStyle(self):
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
        QLineEdit, QCheckBox {
            padding: 5px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QPushButton#add_button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
        }
        QPushButton#add_button:hover {
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
