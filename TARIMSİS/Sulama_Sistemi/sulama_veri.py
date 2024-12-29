import sqlite3
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import seaborn as sns

# Veritabanından verileri çekme
def fetch_data():
    conn = sqlite3.connect(r'veritabanları\irrigation_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM irrigation_log")
    data = cursor.fetchall()
    conn.close()
    return data

# Aylık verileri hesapla
def calculate_monthly_data(data):
    monthly_data = {}
    for row in data:
        plant_type = row[1]
        soil_moisture = row[2]
        start_time = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")
        
        # Veritabanındaki 'end_time' boşsa atla
        if row[4] is None:
            continue
            
        end_time = datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S")
        irrigation_duration = (end_time - start_time).seconds / 60  # Dakika cinsinden
        
        month_year = start_time.strftime("%Y-%m")

        if month_year not in monthly_data:
            monthly_data[month_year] = {
                'total_irrigation_duration': 0,
                'total_irrigations': 0,
                'total_soil_moisture': 0,
                'plant_types': {}
            }
        
        monthly_data[month_year]['total_irrigation_duration'] += irrigation_duration
        monthly_data[month_year]['total_irrigations'] += 1
        monthly_data[month_year]['total_soil_moisture'] += soil_moisture

        if plant_type not in monthly_data[month_year]['plant_types']:
            monthly_data[month_year]['plant_types'][plant_type] = 0
        monthly_data[month_year]['plant_types'][plant_type] += irrigation_duration

    return monthly_data

# Grafik oluşturma fonksiyonu
def show_graph(graph_type, data):
    monthly_data = calculate_monthly_data(data)
    months = sorted(monthly_data.keys())

    plt.style.use('dark_background')  # Koyu tema kullanımı
    plt.figure(figsize=(10, 6))

    if graph_type == "Aylık Sulama Süresi":
        durations = [monthly_data[month]['total_irrigation_duration'] for month in months]
        sns.barplot(x=months, y=durations, palette='magma')  # Seaborn bar grafiği
        plt.title("Aylık Toplam Sulama Süresi (dakika)", fontsize=16)
        plt.xlabel("Ay", fontsize=12)
        plt.ylabel("Süre (dakika)", fontsize=12)

    elif graph_type == "Nem Karşılaştırması":
        moisture_levels = [monthly_data[month]['total_soil_moisture'] / monthly_data[month]['total_irrigations'] for month in months]
        sns.lineplot(x=months, y=moisture_levels, marker='o', palette='coolwarm')  # Seaborn line plot
        plt.title("Aylık Ortalama Toprak Nem Seviyesi", fontsize=16)
        plt.xlabel("Ay", fontsize=12)
        plt.ylabel("Nem Seviyesi", fontsize=12)

    elif graph_type == "Sulama Başlangıç ve Bitiş":
        durations = [(datetime.strptime(row[4], "%Y-%m-%d %H:%M:%S") - datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S")).seconds / 60 for row in data if row[4] is not None]
        sns.histplot(durations, bins=20, color='teal', kde=True)  # Seaborn histogram
        plt.title("Sulama Sürelerinin Dağılımı", fontsize=16)
        plt.xlabel("Süre (dakika)", fontsize=12)
        plt.ylabel("Frekans", fontsize=12)

    elif graph_type == "Aylık Sulama Sayısı":
        counts = [monthly_data[month]['total_irrigations'] for month in months]
        sns.barplot(x=months, y=counts, palette='viridis')  # Seaborn bar plot
        plt.title("Aylık Sulama Sayısı", fontsize=16)
        plt.xlabel("Ay", fontsize=12)
        plt.ylabel("Sulama Sayısı", fontsize=12)

    elif graph_type == "Bitki Türlerine Göre Sulama Süresi":
        plant_types = {}
        for month_data in monthly_data.values():
            for plant, duration in month_data['plant_types'].items():
                if plant not in plant_types:
                    plant_types[plant] = 0
                plant_types[plant] += duration
        plants = list(plant_types.keys())
        durations = list(plant_types.values())
        sns.barplot(x=durations, y=plants, palette='cubehelix')  # Seaborn horizontal bar plot
        plt.title("Bitki Türlerine Göre Sulama Süresi", fontsize=16)
        plt.xlabel("Süre (dakika)", fontsize=12)
        plt.ylabel("Bitki Türleri", fontsize=12)

    elif graph_type == "Aylık Ortalama Toprak Nem":
        moisture_levels = [monthly_data[month]['total_soil_moisture'] / monthly_data[month]['total_irrigations'] for month in months]
        sns.heatmap([moisture_levels], cmap='coolwarm', annot=True, cbar=True)  # Seaborn Heatmap
        plt.title("Aylık Ortalama Toprak Nem Değişimi", fontsize=16)
        plt.xlabel("Ay", fontsize=12)
        plt.ylabel("Ortalama Nem Seviyesi", fontsize=12)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# GUI Oluşturma
def create_gui():
    data = fetch_data()
    root = tk.Tk()
    root.title("Sulama Verileri Analizi")
    root.configure(bg='#1a1a1a')  # Koyu arkaplan

    frame = tk.Frame(root, bg='#1a1a1a')
    frame.pack(pady=20)

    # Grafik Gösterme Düğmeleri
    button_texts = [
        "Aylık Sulama Süresi",
        "Nem Karşılaştırması",
        "Sulama Başlangıç ve Bitiş",
        "Aylık Sulama Sayısı",
        "Bitki Türlerine Göre Sulama Süresi",
        "Aylık Ortalama Toprak Nem"
    ]

    for i, text in enumerate(button_texts):
        button = tk.Button(
            frame, 
            text=text, 
            command=lambda t=text: show_graph(t, data),
            font=("Arial", 12), 
            fg="white", 
            bg="#333333", 
            activebackground="#555555", 
            relief="solid",
            padx=15, pady=10
        )
        button.grid(row=i // 2, column=i % 2, padx=10, pady=10)

    root.mainloop()

create_gui()
