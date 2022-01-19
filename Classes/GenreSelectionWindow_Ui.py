import sqlite3 as sql

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QStatusBar
from PyQt5 import uic

from Classes.Communicate import Communicate
from Classes.Consts import *


class GenresSelectionWindow(QMainWindow):
    """
    Окно выбора жанров
    """
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.statusBar = QStatusBar()

        self.communicate = Communicate()
        self.db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.cur = self.db.cursor()
        self.genres = list(map(lambda x: x[0], self.cur.execute("""SELECT title FROM Genres""").fetchall()))

        uic.loadUi('Interfaces\\GenreSelectionWindow.ui', self)
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Выбор жанров')
        self.setStatusBar(self.statusBar)

        for genre in self.genres:
            self.GenresListWidget.addItem(genre)
        self.GenresListWidget.itemClicked.connect(self.hide_error)

        self.ConfirmSelectionBtn.clicked.connect(self.confirm_btn_press)

    def confirm_btn_press(self) -> None:
        """
        При нажатии на кнопку ConfirmSelectionBtn излучается сигнал, если выбран хотя бы 1 элемент,
        Иначе показывается ошибка.
        """
        if self.GenresListWidget.selectedItems():
            self.radiate_signal()
            self.close()
        else:
            self.show_error()

    def show_error(self) -> None:
        """
        Показывается сообщение, чтоб человек выбрал хотя бы 1 жанр.
        """
        self.statusBar.showMessage('Выберите хотя бы 1 жанр.')
        self.statusBar.setStyleSheet(f'background-color: {ERROR_COLOR}')

    def hide_error(self) -> None:
        """
        Скрывается сообщение, чтоб человек выбрал хотя бы 1 жанр.
        """
        self.statusBar.showMessage('')
        self.statusBar.setStyleSheet(f'background-color: {NORMAL_WINDOW_COLOR}')

    def radiate_signal(self) -> None:
        """
        Излучение сиганала, если выбран хотя бы 1 элемент.
        """
        self.communicate.signal.emit()

    def get_selected_genres(self) -> list:
        """
        Возвращает список с выбранными жанрами
        """
        selected_genres = []
        for genre in map(lambda i: i.text(), self.GenresListWidget.selectedItems()):
            try:
                selected_genres.append(self.cur.execute("""SELECT genre_id FROM Genres WHERE title = ?""",
                                                        (genre,)).fetchone()[0])
            except TypeError:
                continue

        return selected_genres

    def closeEvent(self, event) -> None:
        self.hide_error()
        self.close()