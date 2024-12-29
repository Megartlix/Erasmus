import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import time
import sqlite3
from threading import Thread

# Global değişkenler
aiMode = False
current_moisture = 0
target_moisture = 700  # Varsayılan hedef nem seviyesi
current_water_percentage = 0

# Başlangıçta boş seri bağlantı
arduino = None

# Veritabanı oluşturma ve bağlantı
conn = sqlite3.connect(r"veritabanları\irrigation_data.db", check_same_thread=False)  # Veritabanı bağlantısını çoklu iş parçacığına uygun yapıyoruz
cursor = conn.cursor()

# Sulama logları için tablo oluşturma


# Tkinter ana pencere
root = tk.Tk()
root.title("Bitki Sulama Sistemi")
root.configure(bg="#2E2E2E")  # Arka plan rengini koyu gri yapıyoruz

# Font ve Renk ayarları
font_style = ("Helvetica", 12)
label_color = "#A8D08D"  # Açık yeşil

# Bitki türleri ve hedef nem seviyeleri
plant_moisture_levels = {
    "Domates": 600,
    "Biber": 1020,
    "Çilek": 700,
    "Marul": 500,
    "Havuç": 600,
    "Salatalık": 750,
    "Elma": 680,
    "Armut": 660,
    "Limon": 620,
    "Üzüm": 700
}

# COM port seçimi için ComboBox
com_ports = [port.device for port in serial.tools.list_ports.comports()]
com_port_label = tk.Label(root, text="COM Port Seçin:", fg=label_color, bg="#2E2E2E", font=font_style)
com_port_label.pack()
com_port_combo = ttk.Combobox(root, values=com_ports, font=font_style)
com_port_combo.pack()

# Bitki seçimi ComboBox
plant_label = tk.Label(root, text="Bitki Türü Seçin:", fg=label_color, bg="#2E2E2E", font=font_style)
plant_label.pack()
plant_combo = ttk.Combobox(root, values=list(plant_moisture_levels.keys()), font=font_style)
plant_combo.pack()

# Nem seviyesi etiketi
moisture_label = tk.Label(root, text="Nem Seviyesi: --", fg=label_color, bg="#2E2E2E", font=font_style)
moisture_label.pack()

# Su tankı doluluk oranı etiketi
water_level_label = tk.Label(root, text="Su Tankı Doluluk Oranı: --%", fg=label_color, bg="#2E2E2E", font=font_style)
water_level_label.pack()

# Veritabanı kaydı için fonksiyon (Ana iş parçacığına taşındı)
def log_irrigation(tur, nem, başlama_zamanı, bitiş_zamanı):
    root.after(0, insert_log_into_db, tur, nem, başlama_zamanı, bitiş_zamanı)

# Veritabanına kayıt ekleme işlemi
def insert_log_into_db(tur, nem, başlama_zamanı, bitiş_zamanı):
    cursor.execute("INSERT INTO bitki(tur, nem, başlama_zamanı, bitiş_zamanı) VALUES (?, ?, ?, ?)",
                   (tur, nem, başlama_zamanı, bitiş_zamanı))
    conn.commit()

# COM port bağlantı fonksiyonu
def connect_com_port():
    global arduino
    selected_port = com_port_combo.get()
    try:
        arduino = serial.Serial(selected_port, 9600, timeout=1)
        messagebox.showinfo("Bağlantı", f"{selected_port} portuna bağlanıldı.")
    except serial.SerialException:
        messagebox.showerror("Bağlantı Hatası", f"{selected_port} portuna bağlanılamadı.")

# Manuel sulama fonksiyonları
def start_irrigation():
    global aiMode
    if arduino:
        arduino.write(b'S\n')
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        plant = plant_combo.get()
        log_irrigation(plant, current_moisture, start_time, None)
        print("Sulama başladı")
        aiMode = False  # Manuel sulama sırasında AI modu devre dışı
    else:
        messagebox.showwarning("Bağlantı Hatası", "Önce bir COM portu seçin ve bağlanın.")

def stop_irrigation():
    global aiMode
    if arduino:
        arduino.write(b'T\n')
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        plant = plant_combo.get()
        cursor.execute("UPDATE bitki SET bitiş_zamanı = ? WHERE tur = ? AND bitiş_zamanı IS NULL",
                       (end_time, plant))
        conn.commit()
        print("Sulama durdu")
        aiMode = False  # Manuel sulama sırasında AI modu devre dışı

# Yapay zeka destekli sulama
def ai_controlled_irrigation():
    global aiMode, target_moisture
    if arduino:
        aiMode = True
        target_moisture = plant_moisture_levels.get(plant_combo.get(), 700)
        arduino.write(f"A{target_moisture}\n".encode())

        # Bitki türünü ve nem seviyesini kaydetme
        plant = plant_combo.get()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        log_irrigation(plant, target_moisture, start_time, None)

        print(f"Yapay zeka destekli sulama başladı. Bitki: {plant}, Hedef Nem: {target_moisture}")

def disable_ai():
    global aiMode
    if arduino:
        aiMode = False
        arduino.write(b'D\n')
        print("Yapay zeka destekli sulama durduruldu")

# Nem seviyesini güncelleme işlevi
def update_moisture():
    global current_moisture, aiMode, target_moisture, current_water_percentage
    while True:
        if arduino and arduino.in_waiting > 0:
            try:
                line = arduino.readline().decode().strip()
                if line.startswith("S:"):
                    current_moisture = int(line[2:])
                    moisture_label.config(text=f"Nem Seviyesi: {current_moisture}")
                    # Nem seviyesini kontrol edip işlem yapma
                    if aiMode and current_moisture < target_moisture:
                        arduino.write(b'S\n') # Sulamayı başlat
                    elif aiMode and current_moisture >= target_moisture:
                        arduino.write(b'T\n') # Sulamayı durdur
                elif line.startswith("U:"):
                    current_water_percentage = int(line[2:])
                    water_level_label.config(text=f"Su Tankı Doluluk Oranı: {current_water_percentage}%")
            except ValueError:
                pass
        time.sleep(1)

# Bitki türüne göre nem eşiğini ayarlayan fonksiyon
def set_plant_moisture_level():
    selected_plant = plant_combo.get()
    target_moisture = plant_moisture_levels.get(selected_plant, 700)
    if arduino:
        arduino.write(f"M{target_moisture}\n".encode())
        print(f"{selected_plant} için nem eşiği {target_moisture} olarak ayarlandı")

# Soru-Cevap Kısmı
def ask_question():
    question = question_entry.get().lower()
    answer = ""
    if "sulama" in question:
        answer = "Sulama işlemi bitki türüne ve nem seviyesine göre yapılmaktadır."
    elif "bitki" in question:
        answer = "Farklı bitkiler için hedef nem seviyeleri bulunmaktadır."
    else:
        answer = "Bu konuda yardımcı olamıyorum."
    answer_label.config(text=f"Cevap: {answer}")

# Soru-Cevap Kısmı Arayüz Elemanları
question_label = tk.Label(root, text="Soru Sor:", fg=label_color, bg="#2E2E2E", font=font_style)
question_label.pack()
question_entry = tk.Entry(root, width=50, font=font_style)
question_entry.pack()
ask_button = tk.Button(root, text="Sor", command=ask_question, bg="#4CAF50", fg="white", font=font_style)
ask_button.pack()
answer_label = tk.Label(root, text="Cevap: --", fg=label_color, bg="#2E2E2E", font=font_style)
answer_label.pack()

# COM port bağlan butonu
connect_button = tk.Button(root, text="Bağlan", command=connect_com_port, bg="#4CAF50", fg="white", font=font_style)
connect_button.pack()

# Tabloda sulama işlemi kaydı görüntüleme
def update_log_table():
    for row in cursor.execute("SELECT tur, başlama_zamanı, bitiş_zamanı FROM bitki"):
        log_table.insert("", "end", values=row)

# Sulama loglarını görüntüleyen tablo
log_table = ttk.Treeview(root, columns=("Bitki Türü", "Başlama Zamanı", "Bitiş Zamanı"), show="headings")
log_table.heading("Bitki Türü", text="Bitki Türü")
log_table.heading("Başlama Zamanı", text="Başlama Zamanı")
log_table.heading("Bitiş Zamanı", text="Bitiş Zamanı")
log_table.pack()
update_log_table()

# Butonlar
start_button = tk.Button(root, text="Manuel Başlat", command=start_irrigation, bg="#4CAF50", fg="white", font=font_style)
start_button.pack()
stop_button = tk.Button(root, text="Manuel Durdur", command=stop_irrigation, bg="#f44336", fg="white", font=font_style)
stop_button.pack()
ai_button = tk.Button(root, text="Yapay Zeka Destekli Sulama Başlat", command=lambda: Thread(target=ai_controlled_irrigation).start(), bg="#2196F3", fg="white", font=font_style)
ai_button.pack()
disable_ai_button = tk.Button(root, text="Yapay Zeka Destekli Sulama Durdur", command=disable_ai, bg="#ff9800", fg="white", font=font_style)
disable_ai_button.pack()

# Nem seviyesini güncelleyen thread başlat
Thread(target=update_moisture, daemon=True).start()

# Arayüzü başlat
root.mainloop()