from roboflow import Roboflow
import sqlite3
import os

con = sqlite3.connect("yemekTarifleri.db")
cursor = con.cursor()


def tabloOlustur():
    cursor.execute("CREATE TABLE IF NOT EXISTS yemekTarifleri (ad TEXT, icindekiler TEXT, tarifi TEXT, ulke TEXT, image_path TEXT)")
    # yemekTarifleri tablosunu oluşturur (varsa oluşturmaz)


def veriKarsilastir():
    with open("sinif_degerleri.txt", "r", encoding="UTF-8") as dosya:
        sinif_degerleri = dosya.readlines()

    eslesen_veriler = {}  # Eşleşen verileri, eşleşme sayılarını ve gereken malzemeleri tutmak için bir sözlük oluştur

    for sinif_degeri in sinif_degerleri:
        icindekiler = sinif_degeri.strip().split("-")  # Değerleri "-" karakterine göre ayır

        for icindeki in icindekiler:
            cursor.execute(
                "SELECT * FROM yemekTarifleri WHERE icindekiler LIKE ?", ('%' + icindeki.strip() + '%',))
            veriler = cursor.fetchall()

            for veri in veriler:
                if veri in eslesen_veriler:
                    eslesen_veriler[veri]["eslesme_sayisi"] += 1  # Eşleşme sayısını artır
                    eslesen_veriler[veri]["eslesmeyi_saglayan_veriler"].append(sinif_degeri.strip())  # Eşleşmeyi sağlayan veriyi ekle
                else:
                    eslesen_veriler[veri] = {
                        "eslesme_sayisi": 1,
                        "eslesmeyi_saglayan_veriler": [sinif_degeri.strip()]
                    }  # Yeni eşleşme ekle

    eslesen_veriler = sorted(eslesen_veriler.items(), key=lambda x: x[1]["eslesme_sayisi"], reverse=True)  # Eşleşme sayısına göre sırala

    with open("eslesen_veriler.txt", "w", encoding="UTF-8") as dosya:
        for veri, veri_bilgileri in eslesen_veriler:
            gereken_malzemeler = list(set(veri[1].split("-")) - set(veri_bilgileri["eslesmeyi_saglayan_veriler"]))  # Gereken malzemeleri hesapla
            gereken_malzemeler = [malzeme for malzeme in gereken_malzemeler if malzeme.strip() != ""]  # Boşlukları temizle

            veri_str = "Ad: " + veri[0] + "\n" + \
                       "İçindekiler: " + ", ".join(gereken_malzemeler) + "\n" + \
                       "Ülke: " + veri[3] + "\n" + \
                       "Eşleşme Sayısı / Öneri Önceliği: " + str(veri_bilgileri["eslesme_sayisi"]) + "\n" + \
                       "Mevcut Malzemeleriniz: " + ", ".join(veri_bilgileri["eslesmeyi_saglayan_veriler"]) + "\n" + \
                       "---\n"
            dosya.write(veri_str)  # Eldeki malzemelerin en çok kullanıldığı tarifler

    con.close()


tabloOlustur()
# yemekTarifleri tablosunu oluştur

open("sinif_degerleri.txt", "w").close()

rf = Roboflow(api_key="BWBLSq2jVLdubAWz4sbD")
project = rf.workspace().project("customdetection2")
model = project.version(1).model

folder_path = "./uploads"

file_list = os.listdir(folder_path)
file_list.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)

if file_list:
    image_path = os.path.join(folder_path, file_list[0])
    response = model.predict(image_path, confidence=40, overlap=30)
    predictions = response.json()['predictions']
    class_values = [prediction['class'] for prediction in predictions]

    existing_values = set()

    try:
        with open("sinif_degerleri.txt", "r", encoding="UTF-8") as dosya:
            existing_values = set(dosya.read().splitlines())
    except FileNotFoundError:
        pass

    open("sinif_degerleri.txt", "w").close()

    with open("sinif_degerleri.txt", "a", encoding="UTF-8") as dosya:
        for sinif_degeri in class_values:
            if sinif_degeri not in existing_values:
                dosya.write(sinif_degeri + "\n")
                existing_values.add(sinif_degeri)

    veriKarsilastir()
# Sınıf değerlerini karşılaştır ve sonuçları işle
