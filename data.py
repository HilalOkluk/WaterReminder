import datetime

from datetime import datetime
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QLabel, QProgressBar
from logic import ReminderLogic, WaterTracker


def kaydet_ve_sifirla(su_miktari_bardak):
    simdi = datetime.datetime.now()
    tarih_saat = simdi.strftime("%Y-%m-%d %H:%M")
    print(su_miktari_bardak)

    kaydedilecek_metin = f"[{tarih_saat}] - {su_miktari_bardak} bardak\n"

    dosya_adi = "gunlukmiktar.txt"
    with open(dosya_adi, "a", encoding="utf-8") as dosya:
        dosya.write(kaydedilecek_metin)

    print(f"Su miktarı ({su_miktari_bardak} ml), '{dosya_adi}' dosyasına başarıyla kaydedildi.")

