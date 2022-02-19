import sys
from PyQt5.QtWidgets import QApplication

from Classes.UserWindow import UserWindow


if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setStyle('Fusion')
    StWin = UserWindow()
    StWin.show()
    sys.exit(App.exec_())
