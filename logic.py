from datetime import datetime

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

# Su Hatırlatıcı Zamanlayıcı Mantığı Sınıfı
class ReminderLogic(QObject):
    timeout_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.reminder_timer = QTimer(self)
        self.reminder_timer.setSingleShot(True)
        self.reminder_timer.timeout.connect(self._handle_timeout)

        # Son içme zamanını tutmak için bir değişken ekliyoruz
        self.last_drink_time = datetime.now()

    def start_timer(self, interval_ms):
        if interval_ms <= 0:
            return
        self.reminder_timer.setInterval(interval_ms)
        self.reminder_timer.start()


    def stop_timer(self):
        self.reminder_timer.stop()

    def _handle_timeout(self):

        self.timeout_signal.emit()

    # En son ne zaman su içildiğini kaydetme
    def last_drink(self):
        self.last_drink_time = datetime.now()

    #Son içilen zamandan bu yana geçen süreyi dakika cinsinden hesaplar
    def get_last_time(self):
        now = datetime.now()
        gecen_sure = now - self.last_drink_time

        # Toplam saniyeyi alıp dakika cinsine çeviriyoruz
        minutes_sure = int(gecen_sure.total_seconds() / 60)
        return minutes_sure


# Su Tüketimi ve Hesaplama Mantığı Sınıfı
class WaterTracker:
    def __init__(self, daily_goal):
        self.daily_goal = daily_goal
        self.cups_drunk = 0

    def add_cup(self):
        self.cups_drunk += 1
        self.cupCount()

    def reset_cups(self):
        self.cups_drunk = 0

    def cupCount(self):
        return self.cups_drunk

