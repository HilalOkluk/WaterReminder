from datetime import datetime
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QLabel, QProgressBar

from logic import ReminderLogic, WaterTracker


class WaterReminder(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('panel.ui', self)

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
        if self.tracker_logic.cups_drunk >= self.tracker_logic.daily_goal:
            self.show_tebrik_message()

    def refresh_ui(self):
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

        # ProgressBar'ı sıfırlıyoruz
        if self.progressTimer:
            self.progressTimer.setValue(0)

        reply = QMessageBox.question(self,
                                     "Su Hatırlatıcısı",
                                     "Su içme vakti! Bir bardak su içtiniz mi?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.add_cup()
        else:
            self.start_reminder()

        # Tebrik Mesajı
    def show_tebrik_message(self):

        self.stop_reminder()  # Geri sayımı durdur
        QMessageBox.information(self,
                                "Hedefe Ulaşıldı!",
                                "Tebrikler! Günlük su içme hedefinize ulaştınız. Harika bir iş çıkardın!")

