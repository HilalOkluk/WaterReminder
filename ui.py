from datetime import datetime
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QLabel, QProgressBar

from logic import ReminderLogic, WaterTracker
from data import kaydet_ve_sifirla


class WaterReminder(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('panel.ui', self)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

        self.btnStart.clicked.connect(self.start_reminder)
        self.btnAddCup.clicked.connect(self.add_cup)
        self.btnStop.clicked.connect(self.stop_reminder)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(1000)

        self.reminder_logic = ReminderLogic(self)
        self.reminder_logic.timeout_signal.connect(self.show_reminder_message)

        self.tracker_logic = WaterTracker(self.spinGoal.value())
        self.spinGoal.valueChanged.connect(self.update_goal)

        self.remaining_time_seconds = 0
        self.is_paused_for_sleep = False

        # ProgressBar'ı tanımlıyoruz.
        self.progressTimer = self.findChild(QProgressBar,
                                            'Timer')
        if self.progressTimer:
            self.progressTimer.setMaximum(0)
            self.progressTimer.setValue(0)

            # İçilen su miktarını gösterecek QLabel objesini buluyoruz
        self.lblCupCount = self.findChild(QLabel, 'lblCup')
        if self.lblCupCount:
            self.lblCupCount.setText(f"İçilen Bardak: {self.tracker_logic.cups_drunk}")




    def update_goal(self):
        self.tracker_logic.daily_goal = self.spinGoal.value()
        self.update_progress_bar()

    def start_reminder(self):
        self.lblStatus.setText("Başlatıldı")
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)

        aralik_saniye = self.spinInterval.value()
        interval_ms = aralik_saniye * 1000

        self.remaining_time_seconds = aralik_saniye
        self.reminder_logic.start_timer(interval_ms)

        # ProgressBar'ı başlangıç değerlerine ayarlıyoruz
        if self.progressTimer:
            self.progressTimer.setMaximum(aralik_saniye)
            self.progressTimer.setValue(aralik_saniye)

    def stop_reminder(self):
        self.lblStatus.setText("Durduruldu")
        self.btnStop.setEnabled(False)
        self.btnStart.setEnabled(True)
        self.reminder_logic.stop_timer()

        self.remaining_time_seconds = 0
        if self.lblTimer:
            self.lblTimer.setText("Durduruldu")

        # ProgressBar'ı sıfırlıyoruz
        if self.progressTimer:
            self.progressTimer.setValue(0)

    def add_cup(self):
        self.lblStatus.setText("1 Bardak İçtim")

        self.tracker_logic.add_cup()
        self.update_progress_bar()
        self.update_cup_count_label()

        aralik_saniye = self.spinInterval.value()
        interval_ms = aralik_saniye * 1000
        self.reminder_logic.start_timer(interval_ms)
        self.remaining_time_seconds = aralik_saniye

        # ProgressBar'ı yeni aralığa göre ayarlama
        if self.progressTimer:
            self.progressTimer.setMaximum(aralik_saniye)
            self.progressTimer.setValue(aralik_saniye)

        # Hedefe ulaşıldığında tebrik mesajı göster
        if self.tracker_logic.cups_drunk == self.tracker_logic.daily_goal:
            self.show_tebrik_message()

    def refresh_ui(self):

        simdi = datetime.now()

        if simdi.hour == 0 and simdi.minute == 0 and simdi.second == 0:
            self.kaydet()


        #nowTime = datetime.now()
        #if nowTime.strftime("%H:%M:%S") == "18:41:00":
            #self.reset()

        if self.reminder_logic.reminder_timer.isActive() and self.remaining_time_seconds > 0:
            self.remaining_time_seconds -= 1
            if self.lblTimer:
                self.lblTimer.setText(f"Kalan Süre: {self.remaining_time_seconds} sn")

        # ProgressBar'ı güncelliyoruz
        if self.progressTimer:
                self.progressTimer.setValue(self.remaining_time_seconds)

    def update_progress_bar(self):
        hedef = self.spinGoal.value()
        yuzde = self.progress.value()
        self.progress.setMaximum(hedef)
        self.progress.setValue(yuzde + 1)

        # İçilen su miktarını gösteren fonksiyon
    def update_cup_count_label(self):

        if self.lblCupCount:
            self.lblCupCount.setText(f"İçilen Bardak: {self.tracker_logic.cups_drunk}")


    def show_reminder_message(self):
            self.lblStatus.setText("Süre doldu!")
            self.reminder_logic.stop_timer()


            # Pop-up'ı gösterecek ve 10 saniye sonra otomatik kapanacak
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("Su Hatırlatıcısı")
            msgBox.setText("Su içme vakti! Bir bardak su içtiniz mi?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            # Yeni bir QTimer oluşturuyoruz
            popup_timer = QTimer(self)
            popup_timer.setSingleShot(True)
            popup_timer.setInterval(5000)  # 5 saniye sonra zamanlayıcıyı çalıştır

            def handle_timeout():
                self.start_reminder()

            popup_timer.timeout.connect(handle_timeout)
            popup_timer.start()

            # Pop-up'ı göster ve kullanıcı bir butona basana kadar bekle
            reply = msgBox.exec_()

            # Zamanlayıcıyı durdur, çünkü kullanıcı bir butona bastı
            if popup_timer.isActive():
                popup_timer.stop()

            if reply == QMessageBox.Yes:
                self.add_cup()
            else:
                self.start_reminder()


        # Tebrik Mesajı
    def show_tebrik_message(self):


        QMessageBox.information(self,
                                "Hedefe Ulaşıldı!",
                                "Tebrikler! Günlük su içme hedefinize ulaştınız. Harika bir iş çıkardın!")

        # Yeni eklenen fonksiyon

    def reset(self):
        self.tracker_logic.sıfırlama()
        self.progress.setValue(0)
        self.lblStatus.setText(self.tracker_logic.status)
        self.lblCupCount.setText(f"İçilen Bardak: {self.tracker_logic.cups_drunk}")
        self.reminder_logic.stop_timer()
        if self.progressTimer:
            self.progressTimer.setValue(0)
            self.progressTimer.setMaximum(0)

        self.lblTimer.setText(" ")

        self.btnStart.setEnabled(True)
        self.btnStop.setEnabled(False)

    def kaydet(self):

        # Güncel bardak sayısını kaydetme fonksiyonuna gönderiyoruz.
        kaydet_ve_sifirla(self.tracker_logic.cups_drunk)
        #Bardak sayısını sıfırlama
        self.tracker_logic.reset_cups()
        self.update_cup_count_label()
        self.update_progress_bar()


