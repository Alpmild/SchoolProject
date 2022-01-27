import sys
from PyQt5.QtWidgets import QApplication

from Classes.AdminWindow_Ui import AdminWindow
# from Classes.StartWindow_Ui import StartWindow


if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setStyle('Fusion')
    StWin = AdminWindow()
    StWin.show()
    sys.exit(App.exec_())
