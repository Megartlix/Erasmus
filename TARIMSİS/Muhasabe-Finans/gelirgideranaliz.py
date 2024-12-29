import sys
import sqlite3
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QComboBox, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mplcursors

# Veritabanı bağlantısı ve veri çekme fonksiyonları
def get_gelir_data(time_period='monthly'):
    conn = sqlite3.connect('veritabanları\gelirler.db')
    cursor = conn.cursor()
    
    if time_period == 'monthly':
        cursor.execute("SELECT strftime('%Y-%m', tarih) AS month, SUM(gelir) FROM gelirler GROUP BY month")
    elif time_period == 'daily':
        cursor.execute("SELECT tarih, gelir FROM gelirler")
    
    data = cursor.fetchall()
    conn.close()
    return data

def get_gider_data(time_period='monthly'):
    conn = sqlite3.connect('veritabanları\gelirler.db')
    cursor = conn.cursor()

    if time_period == 'monthly':
        cursor.execute("SELECT strftime('%Y-%m', tarih) AS month, SUM(gider) FROM giderler GROUP BY month")
    elif time_period == 'daily':
        cursor.execute("SELECT tarih, gider FROM giderler")
    
    data = cursor.fetchall()
    conn.close()
    return data

# PyQt5 Ana Pencere
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gelir ve Gider Analizi")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        layout = QVBoxLayout()

        # Grafik Canvas'ı
        self.canvas = FigureCanvas(plt.figure(figsize=(8, 6)))
        layout.addWidget(self.canvas)

        # Grafik Türü Seçim
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItem("Çubuk Grafiği")
        self.graph_type_combo.addItem("Pasta Grafiği")
        self.graph_type_combo.addItem("Çizgi Grafiği")
        self.graph_type_combo.addItem("Alan Grafiği")
        self.graph_type_combo.currentIndexChanged.connect(self.update_graph)
        layout.addWidget(self.graph_type_combo)

        # Zaman Dilimi Seçimi
        self.time_period_combo = QComboBox()
        self.time_period_combo.addItem("Aylık")
        self.time_period_combo.addItem("Günlük")
        self.time_period_combo.currentIndexChanged.connect(self.update_graph)
        layout.addWidget(self.time_period_combo)

        # Ana Widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Uygulama başladığında varsayılan grafiği ayarla
        self.update_graph()

    # Grafik Güncelleme Fonksiyonu
    def update_graph(self):
        # Grafik türü ve zaman dilimi seçimlerini al
        graph_type = self.graph_type_combo.currentText()
        time_period = self.time_period_combo.currentText().lower()

        # Verileri al
        gelir_data = get_gelir_data(time_period)
        gider_data = get_gider_data(time_period)

        # Veriyi işleme
        gelir_x = [x[0] for x in gelir_data]
        gelir_y = [x[1] for x in gelir_data]
        gider_x = [x[0] for x in gider_data]
        gider_y = [x[1] for x in gider_data]

        # Grafiği çizme
        fig = self.canvas.figure
        ax = fig.add_subplot(111)
        ax.clear()

        if graph_type == "Çubuk Grafiği":
            ax.bar(gelir_x, gelir_y, label="Gelirler", color='green', alpha=0.6)
            ax.bar(gider_x, gider_y, label="Giderler", color='red', alpha=0.6)
        elif graph_type == "Pasta Grafiği":
            ax.pie(gelir_y, labels=gelir_x, autopct='%1.1f%%', startangle=140)
            plt.title("Gelirler")
            fig.add_subplot(122).pie(gider_y, labels=gider_x, autopct='%1.1f%%', startangle=140)
            plt.title("Giderler")
        elif graph_type == "Çizgi Grafiği":
            ax.plot(gelir_x, gelir_y, label="Gelirler", color='green', marker='o')
            ax.plot(gider_x, gider_y, label="Giderler", color='red', marker='x')
        elif graph_type == "Alan Grafiği":
            ax.fill_between(gelir_x, gelir_y, color='green', alpha=0.3, label="Gelirler")
            ax.fill_between(gider_x, gider_y, color='red', alpha=0.3, label="Giderler")

        ax.set_title("Gelir ve Gider Analizi")
        ax.set_xlabel("Zaman")
        ax.set_ylabel("Miktar")
        ax.legend()

        # Grafik etkileşimi (fare ile veri gösterimi)
        mplcursors.cursor(hover=True)

        # Grafiği güncelle
        self.canvas.draw()

# Uygulamayı başlatma
def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_app()