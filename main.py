import sys
from PyQt5 import QtWidgets
from ui import WaterReminder

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = WaterReminder()
    w.show()
    sys.exit(app.exec_())