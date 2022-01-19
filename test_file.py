import sys
from PyQt5.QtWidgets import QApplication

from Classes.StartWindow_Ui import StartWindow
from Classes.FilmSelectionWindow_Ui import FilmSelectionWindow


if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setStyle('Fusion')
    StWin = FilmSelectionWindow()
    StWin.show()
    sys.exit(App.exec_())
