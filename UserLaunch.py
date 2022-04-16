from sys import argv, exit
from PyQt5.QtWidgets import QApplication

from data.UserWindow import UserWindow


if __name__ == '__main__':
    App = QApplication(argv)
    App.setStyle('Fusion')
    StWin = UserWindow()
    StWin.show()
    exit(App.exec_())
