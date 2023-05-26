import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import atexit
import subprocess
from tkinter import ttk
import sqlite3
import cv2
from PIL import Image, ImageTk


def resim_sec():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg; *.jpeg; *.png")])
    if file_path:
        hedef_klasor = os.path.join(os.getcwd(), "uploads")

        try:
            os.makedirs(hedef_klasor, exist_ok=True)
            dosya_adi = os.path.basename(file_path)
            hedef_yol = os.path.join(hedef_klasor, dosya_adi)
            shutil.copy(file_path, hedef_yol)
            bilgi.config(text="Resim başarılı bir şekilde yüklendi.")
        except shutil.Error as e:
            bilgi.config(text="Hata: " + str(e))


def klasoru_temizle():
    hedef_klasor = os.path.join(os.getcwd(), "uploads")
    for dosya in os.listdir(hedef_klasor):
        dosya_yolu = os.path.join(hedef_klasor, dosya)
        if os.path.isfile(dosya_yolu):
            os.remove(dosya_yolu)
    if 'bilgi' in globals():
        bilgi.config(text="uploads klasörü temizlendi.")



def verileri_goster():
    # 100epochs.py dosyasını çalıştır
    run_100epochs()

    hedef_klasor = os.path.join(os.getcwd(), "eslesen_veriler.txt")

    try:
        with open(hedef_klasor, "r", encoding="utf-8") as dosya:
            veriler = dosya.readlines()
            if not veriler:
                veri_kutusu.delete(1.0, tk.END)  # Metin kutusunu temizle
                bilgi.config(text="Öneri bulunamadı.")
                return
            veri_kutusu.delete(1.0, tk.END)  # Metin kutusunu temizle
            combo_values = []  # Combobox değerlerini tutmak için boş bir liste
            for veri in veriler:
                if "Ad" in veri:  # Sadece "Ad" içeren kısımları kırmızı renkte göster
                    veri_kutusu.insert(tk.END, veri, "kirmizi")
                    combo_values.append(veri.split(":")[1].strip())  # "Ad" kısmını combo_values listesine ekle
                else:
                    veri_kutusu.insert(tk.END, veri)
            combo_box['values'] = combo_values  # Combo box değerlerini güncelle
            veri_kutusu.tag_config("kirmizi", foreground="red")  # "kirmizi" tag rengini ayarla
    except FileNotFoundError:
        bilgi.config(text="Dosya bulunamadı.")


def tarifi_goster():

    secilen_tarif = combo_box.get()
    if secilen_tarif:
        conn = sqlite3.connect("yemekTarifleri.db")
        cursor = conn.cursor()
        cursor.execute("SELECT tarifi FROM yemekTarifleri WHERE Ad=?", (secilen_tarif,))
        tarif = cursor.fetchone()
        conn.close()

        if tarif:

            def tarifi_goster():
                global secilen_tarif
                secilen_tarif = combo_box_tarif.get()
                if secilen_tarif:
                    conn = sqlite3.connect("yemekTarifleri.db")
                    cursor = conn.cursor()
                    cursor.execute("SELECT tarifi, image_path FROM yemekTarifleri WHERE Ad=?", (secilen_tarif,))
                    tarif, image_path = cursor.fetchone()
                    conn.close()

                    if tarif:
                        tarif_metin.config(state="normal")
                        tarif_metin.delete(1.0, tk.END)
                        tarif_metin.insert(tk.END, tarif)
                        tarif_metin.config(state="disabled")

                        resim_frame_sol = tk.Frame(tarif_arayuz, width=600, height=200)
                        resim_frame_sol.place(relx=0, rely=0, anchor="nw")

                        resim_frame_sag = tk.Frame(tarif_arayuz, width=600, height=200)
                        resim_frame_sag.place(relx=1, rely=0, anchor="ne")

                        for i, path in enumerate(image_path.split(',')):
                            try:
                                resim = Image.open(path)
                                resim = resim.resize((150, 150), Image.ANTIALIAS)
                                resim = ImageTk.PhotoImage(resim)

                                resim_label_sol = tk.Label(resim_frame_sol, image=resim)
                                resim_label_sol.image = resim
                                resim_label_sol.grid(row=0, column=i, padx=10, pady=10)

                                resim_label_sag = tk.Label(resim_frame_sag, image=resim)
                                resim_label_sag.image = resim
                                resim_label_sag.grid(row=0, column=i, padx=10, pady=10)
                            except FileNotFoundError:
                                print(f"Dosya bulunamadı: {path}")


                    else:
                        bilgi.config(text="Seçilen tarif bulunamadı.")
                else:
                    bilgi.config(text="Lütfen bir tarif seçin.")

            tarif_arayuz = tk.Toplevel(arayuz)
            tarif_arayuz.title("Tarif Sayfası")
            tarif_arayuz.geometry("850x650")
            tarif_arayuz.update_idletasks()

            # Ekranın ortasında konumlandırma
            window_width = tarif_arayuz.winfo_width()
            window_height = tarif_arayuz.winfo_height()
            screen_width = tarif_arayuz.winfo_screenwidth()
            screen_height = tarif_arayuz.winfo_screenheight()
            x_coordinate = int((screen_width / 2) - (window_width / 2))
            y_coordinate = int((screen_height / 2) - (window_height / 2))
            tarif_arayuz.geometry(f"850x650+{x_coordinate}+{y_coordinate}")
            tarif_arayuz.resizable(False, False)

            background_image = tk.PhotoImage(file="arkaplan/ap.jpg")
            background_label = tk.Label(tarif_arayuz, image=background_image)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)

            tarif_conternir = tk.Frame(tarif_arayuz, width=600, height=250)
            tarif_conternir.place(relx=0.5, rely=0.6, anchor="center")

            scrollbar = tk.Scrollbar(tarif_conternir)
            scrollbar.pack(side="right", fill="y")

            tarif_metin = tk.Text(tarif_conternir, width=100, height=26, yscrollcommand=scrollbar.set, state="disabled")
            tarif_metin.pack(side="left", padx=10, pady=10)

            scrollbar.config(command=tarif_metin.yview)

            tarif_metin.insert(tk.END, tarif[0])
            tarif_metin.config(state="disabled")

            combo_box_tarif = ttk.Combobox(tarif_arayuz, state="readonly")
            combo_box_tarif.set(secilen_tarif)
            combo_box_tarif.pack(padx=10, pady=10)
            combo_box_tarif.config(font=("Arial", 13))

            tarif_goster_button = tk.Button(tarif_arayuz, text="Tarifi Göster", command=tarifi_goster, bg="white",
                                            fg="black",
                                            font=("Arial", 10, "bold"))
            tarif_goster_button.pack(padx=10, pady=10)

            kapat_button = tk.Button(tarif_arayuz, text="Kapat", command=tarif_arayuz.destroy, bg="red", fg="white",
                                     font=("Arial", 10, "bold"))
            kapat_button.place(x=780, y=600)

            conn = sqlite3.connect("yemekTarifleri.db")
            cursor = conn.cursor()
            cursor.execute("SELECT Ad FROM yemekTarifleri")
            tarifler = cursor.fetchall()
            conn.close()

            combo_box_tarif['values'] = [tarif[0] for tarif in tarifler]


def farkli_pencere_ac():
    def resi_cek():
        video_kayit = cv2.VideoCapture(0)
        ret, resim = video_kayit.read()
        video_kayit.release()

        if ret:
            resim_yolu = os.path.join(os.getcwd(), "uploads", "resim.jpg")

            # Çekilen resmi göster
            resim_goster(resim)

            # Resmi kaydetme işlemi
            kaydet_button = tk.Button(yeni_pencere, text="Kaydet", command=lambda: resmi_kaydet(resim, resim_yolu), bg="white", fg="black", font=("Arial", 10, "bold"))
            kaydet_button.place(x=20, y=70)

            bilgi.config(text="Resim çekildi. Kaydetmek için 'Kaydet' butonuna tıklayın.")
        else:
            bilgi.config(text="Hata: Resim çekilemedi.")

    def resim_goster(resim):
        resim = cv2.cvtColor(resim, cv2.COLOR_BGR2RGB)
        resim = Image.fromarray(resim)
        resim = resim.resize((450, 350), Image.ANTIALIAS)
        resim = ImageTk.PhotoImage(resim)

        resim_label = tk.Label(yeni_pencere, image=resim)
        resim_label.image = resim
        resim_label.place(x=100, y=80)

    def resmi_kaydet(resim, resim_yolu):
        cv2.imwrite(resim_yolu, resim)
        bilgi.config(text="Resim başarılı bir şekilde kaydedildi.")

    def kapat():
        yeni_pencere.destroy()

    yeni_pencere = tk.Toplevel(arayuz)
    yeni_pencere.title("Yeni Pencere")
    yeni_pencere.geometry("600x500+1300+0")  # Pencere boyutu ve konumu
    yeni_pencere.resizable(False, False)  # Yeniden boyutlandırılamaz hale getirildi
    yeni_pencere.attributes("-topmost", True)  # Diğer pencerelerin önüne çıkarıldı

    resim_cek_button = tk.Button(yeni_pencere, text="Resim Çek", command=resi_cek, bg="white", fg="black",
                                 font=("Arial", 10, "bold"))
    resim_cek_button.place(x=20, y=20)

    kapat_button = tk.Button(yeni_pencere, text="Kapat", command=kapat, bg="red", fg="white",
                             font=("Arial", 10, "bold"))
    kapat_button.place(x=20, y=120)


def farkli_arayuz_ac():
    yeni_arayuz = tk.Toplevel(arayuz)
    yeni_arayuz.title("Tarif Ekleme Sayfası")
    yeni_arayuz.geometry("850x650")
    yeni_arayuz.resizable(False, False)

    # Etiketler
    lbl_yemek_adi = tk.Label(yeni_arayuz, text="Yemeğin Adı:", font=("Arial", 16))
    lbl_yemek_adi.pack()

    # Giriş Kutusu
    entry_yemek_adi = tk.Entry(yeni_arayuz, font=("Arial", 14))
    entry_yemek_adi.pack()

    # Boşluk
    lbl_bosluk = tk.Label(yeni_arayuz, text="", font=("Arial", 10))
    lbl_bosluk.pack()

    lbl_icerikler = tk.Label(yeni_arayuz, text="İçerikler:", font=("Arial", 16))
    lbl_icerikler.pack()

    entry_icerikler = tk.Entry(yeni_arayuz, font=("Arial", 14))
    entry_icerikler.pack()

    # Boşluk
    lbl_bosluk = tk.Label(yeni_arayuz, text="", font=("Arial", 10))
    lbl_bosluk.pack()

    lbl_tarif = tk.Label(yeni_arayuz, text="Tarif:", font=("Arial", 16))
    lbl_tarif.pack()

    entry_tarif = tk.Text(yeni_arayuz, height=10, width=50, font=("Arial", 12))
    entry_tarif.pack()

    # Boşluk
    lbl_bosluk = tk.Label(yeni_arayuz, text="", font=("Arial", 10))
    lbl_bosluk.pack()

    lbl_ulke = tk.Label(yeni_arayuz, text="Yemeğin Ülkesi:", font=("Arial", 16))
    lbl_ulke.pack()

    entry_ulke = tk.Entry(yeni_arayuz, font=("Arial", 14))
    entry_ulke.pack()

    # Boşluk
    lbl_bosluk = tk.Label(yeni_arayuz, text="", font=("Arial", 10))
    lbl_bosluk.pack()

    lbl_resim_yolu = tk.Label(yeni_arayuz, text="Resim Yolu:", font=("Arial", 16))
    lbl_resim_yolu.pack()

    entry_resim_yolu = tk.Entry(yeni_arayuz, font=("Arial", 14))
    entry_resim_yolu.pack()

    # Scrollbarlı Container
    conternir = tk.Frame(yeni_arayuz)
    conternir.pack(fill="both", expand=True)

    # Kaydet ve Kapat Butonları
    def kaydet():
        yemek_adi = entry_yemek_adi.get()
        icerikler = entry_icerikler.get()
        tarif = entry_tarif.get("1.0", "end-1c")
        ulke = entry_ulke.get()
        resim_yolu = entry_resim_yolu.get()

        # Veritabanı bağlantısı
        conn = sqlite3.connect("yemekTarifleri.db")
        cursor = conn.cursor()

        # Yemek adının veritabanında var olup olmadığını kontrol et
        cursor.execute("SELECT * FROM yemekTarifleri WHERE ad = ?", (yemek_adi,))
        result = cursor.fetchone()

        if result:
            messagebox.showwarning("Uyarı", "Bu isimde bir yemek zaten mevcut.")
        else:
            # Verileri ekle
            cursor.execute(
                "INSERT INTO yemekTarifleri (ad, icindekiler, tarifi, ulke, image_path) VALUES (?, ?, ?, ?, ?)",
                (yemek_adi, icerikler, tarif, ulke, resim_yolu))

            # Veritabanı değişikliklerini kaydet
            conn.commit()

            messagebox.showinfo("Bilgi", "Tarif başarıyla kaydedildi.")

    def kapat():
        yeni_arayuz.destroy()

    btn_kaydet = tk.Button(conternir, text="Kaydet", command=kaydet, font=("Arial", 14))
    btn_kaydet.pack(side="left", padx=10, pady=10)

    btn_kapat = tk.Button(conternir, text="Kapat", command=kapat, bg="red", font=("Arial", 14))
    btn_kapat.pack(side="right", padx=10, pady=10)




def run_100epochs():
    subprocess.run(["python", "100epochs.py"])


def kapat():
    arayuz.destroy()  # Arayüzü kapat


arayuz = tk.Tk()
arayuz.title("Yemek Önerisi")
arayuz.resizable(False, False)  # Arayüzün genişletilemez ve küçültülemez olması

# Arka plan görseli
arkaplan_resim = tk.PhotoImage(file="arkaplan/ap.jpg")
arkaplan = tk.Label(arayuz, image=arkaplan_resim)
arkaplan.pack(side="top", fill="x")

giris = tk.Button(text="Resim seçiniz", command=resim_sec, bg="white", fg="black", font=("Arial", 10, "bold"))
giris.place(x=20, y=50)

farkli_pencere_button = tk.Button(text="Fotograf Çek", command=farkli_pencere_ac, bg="white", fg="black", font=("Arial", 10, "bold"))
farkli_pencere_button.place(x=150, y=50)


goster_button = tk.Button(text="Önerileri Göster", command=verileri_goster, bg="white", fg="black",
                          font=("Arial", 10, "bold"))
goster_button.place(x=20, y=110)

bilgi = tk.Label(arayuz, text="", fg="red")
bilgi.place(x=20, y=80)

veri_kutusu = tk.Text(arayuz, width=100, height=30)
veri_kutusu.place(x=20, y=150)

scrollbar = tk.Scrollbar(arayuz)
scrollbar.place(x=830, y=150, height=450)

veri_kutusu.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=veri_kutusu.yview)

combo_box = ttk.Combobox(arayuz, state="readonly")
combo_box.place(x=180, y=110)

tarif_button = tk.Button(arayuz, text="Tarifi Göster", command=tarifi_goster, bg="white", fg="black",
                         font=("Arial", 10, "bold"))
tarif_button.place(x=340, y=110)

yeni_button = tk.Button(arayuz, text="Yeni Tarif Ekle", command=farkli_arayuz_ac, bg="white", fg="black",
                        font=("Arial", 10, "bold"))
yeni_button.place(x=460, y=110)


kapat_button = tk.Button(text="Kapat", command=kapat, bg="red", fg="white", font=("Arial", 10, "bold"))
kapat_button.place(x=780, y=110)

atexit.register(klasoru_temizle)  # uygulama kapatıldığında klasörü temizle

# Arayüzü ekranın ortasına yerleştirme
window_width = 850
window_height = 650
screen_width = arayuz.winfo_screenwidth()
screen_height = arayuz.winfo_screenheight()
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))
arayuz.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Uygulama ikonunu değiştirme
icon_resim = tk.PhotoImage(file="arkaplan/i1.png")
arayuz.iconphoto(True, icon_resim)

arayuz.mainloop()
