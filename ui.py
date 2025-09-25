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

        #ui'yi saniyede bir güncelleyecek timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_ui)
        self.timer.start(1000)

        #timerın süresi dolduğunda mesaj metodunu tetikler
        self.reminder_logic = ReminderLogic(self)
        self.reminder_logic.timeout_signal.connect(self.show_reminder_message)

        #hedef değiştirildiğinde update eder
        self.tracker_logic = WaterTracker(self.spinGoal.value())
        self.spinGoal.valueChanged.connect(self.update_goal)

        self.remaining_time_seconds = 0
        self.is_paused_for_sleep = False


        self.txtSleepTime = self.findChild(QtWidgets.QLineEdit, 'editQuiet_2')
        self.lblSleepStatus = self.findChild(QLabel, 'lblSleepStatus')

        #başlangıç olarak -1 girdik ki geçersiz olsun. Kullanıcı değiştirdiğinde güncellenecek
        self.sleep_start_hour = -1
        self.sleep_end_hour = -1

        #sessiz saatleri değiştirip enterladığımızda güncelleme
        self.txtSleepTime.returnPressed.connect(self.update_sleep_time)

        # Timer progressi
        self.progressTimer = self.findChild(QProgressBar,
                                            'TimerBar')
        #başlangıçlar 0
        if self.progressTimer:
            self.progressTimer.setMaximum(0)
            self.progressTimer.setValue(0)

            # İçilen su miktarını gösterecek QLabel objesi
        self.lblCupCount = self.findChild(QLabel, 'lblCup')
        if self.lblCupCount:
            self.lblCupCount.setText(f"İçilen Bardak: {self.tracker_logic.cups_drunk}")

    #hedefi güncelleyen metot
    def update_goal(self):

        self.tracker_logic.daily_goal = self.spinGoal.value()
        self.update_progress_bar()


    #timer başladığında  çalışan metot
    def start_reminder(self):

        simdi = datetime.now()

        # Eğer uyku saatleri ayarlandıysa ve mevcut saat bu aralıkta ise
        if self.sleep_start_hour != -1 and self.sleep_end_hour != -1:
            if self.sleep_start_hour <= simdi.hour < self.sleep_end_hour:
                QMessageBox.information(self, "Uyarı", "Uyku modundayken hatırlatıcıyı başlatamazsınız.")
                return

        # Uyku modunda değilsek veya uyku saatleri ayarlanmadıysa normal akış devam eder.
        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)

        aralik_saniye = self.spinInterval.value()
        self.remaining_time_seconds = aralik_saniye
        #timer spinInterval değeri kadar sayacak
        self.reminder_logic.start_timer(aralik_saniye)

        if self.progressTimer:
            self.progressTimer.setMaximum(aralik_saniye)
            self.progressTimer.setValue(aralik_saniye)

    def stop_reminder(self):
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
        # su içildiğinde çalışacak metotlar
        self.tracker_logic.add_cup()
        self.update_progress_bar()
        self.update_cup_count_label()
        self.reminder_logic.last_drink()

        aralik_saniye = self.spinInterval.value()
        self.reminder_logic.start_timer(aralik_saniye)
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
        self.check_sleep_time(simdi)

        #saat 00.00'da günlük içilen miktarı kaydet
        if simdi.hour == 0 and simdi.minute == 0 and simdi.second == 0 :
            self.kaydet()

        #Son içilen süre:devamlı güncelleniyor
        minutes_last_drink = self.reminder_logic.get_last_time()
        if self.lblLastDrink:
            self.lblLastDrink.setText(f"Son İçilen: {minutes_last_drink} dk önce")

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

        #Hatırlatıcı mesajı metodu
    def show_reminder_message(self):

            self.reminder_logic.stop_timer()
            # Pop-up'ı gösterecek ve 10 saniye sonra otomatik kapanacak
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("Su Hatırlatıcısı")
            msgBox.setText("Su içme vakti! Bir bardak su içtiniz mi?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            # Yeni bir QTimer oluşturuyoruz
            popup_timer = QTimer(self)
            popup_timer.setSingleShot(True)
            popup_timer.setInterval(30000)  # 5 saniye sonra zamanlayıcıyı çalıştır

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

    def kaydet(self):
        # Güncel bardak sayısını kaydetme fonksiyonuna gönderiyoruz.
        kaydet_ve_sifirla(self.tracker_logic.cups_drunk)
        #Bardak sayısını sıfırlama
        self.tracker_logic.reset_cups()
        self.update_cup_count_label()
        self.update_progress_bar()

    def check_sleep_time(self, now_time):
        if not self.sleep_start_hour == -1 and not self.sleep_end_hour == -1:
            if self.sleep_start_hour <= now_time.hour < self.sleep_end_hour:
                if not self.is_paused_for_sleep:
                    self.stop_reminder()
                    self.is_paused_for_sleep = True
                    self.lblSleepStatus.setText("Uyku Modu: AKTİF")

            else:
                if self.is_paused_for_sleep:
                    self.is_paused_for_sleep = False
                    self.lblSleepStatus.setText("Uyku Modu: KAPALI")
                    self.start_reminder()

    def update_sleep_time(self):
        try:
            sleep_time_str = self.txtSleepTime.text()
            if not sleep_time_str:
                self.sleep_start_hour = -1
                self.sleep_end_hour = -1
                self.lblSleepStatus.setText("Uyku Modu: KAPALI")
                return

            hours = sleep_time_str.split('-')
            if len(hours) == 2:
                self.sleep_start_hour = int(hours[0].strip())
                self.sleep_end_hour = int(hours[1].strip())
                self.lblSleepStatus.setText(f"Uyku Modu: {self.sleep_start_hour}-{self.sleep_end_hour}")
            else:
                self.lblSleepStatus.setText("Hatalı saat formatı (Örnek: 7-24)")

        except (ValueError, IndexError):
            self.lblSleepStatus.setText("Hatalı saat formatı (Örnek: 7-24)")
            self.sleep_start_hour = -1
            self.sleep_end_hour = -1

        #Saat ayarlandıktan sonra hemen kontrol yap
        self.check_sleep_time(datetime.now())