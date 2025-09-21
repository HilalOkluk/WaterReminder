import sys
from PyQt5 import uic,QtWidgets
from ui import WaterReminder
import datetime

if __name__ == '__main__':
    app=QtWidgets.QApplication(sys.argv)
    w = WaterReminder()
    w.show()
    sys.exit(app.exec_())