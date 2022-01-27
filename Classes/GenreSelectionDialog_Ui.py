import sqlite3 as sql
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic


class GenresSelectionDialog(QDialog):
    """Окно выбора жанров"""
    def __init__(self, parent, tab: int):
        super(GenresSelectionDialog, self).__init__(parent)
        self.parent = parent
        self.tab = tab

        self.db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.cur = self.db.cursor()
        self.genres = list(map(lambda x: x[0], self.cur.execute("""SELECT title FROM Genres""").fetchall()))

        uic.loadUi('Interfaces\\GenresSelectionDialog.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setWindowTitle('Выбор жанров')
        self.setModal(True)

        for genre in self.genres:
            self.GenresListWidget.addItem(genre)

        self.set_btn_status()
        self.GenresListWidget.itemPressed.connect(self.set_btn_status)

        self.ConfirmSelectionBtn.clicked.connect(self.set_genres)

    def set_btn_status(self):
        """Установка статуса кнопки: если выбран хотя бы 1 элемент в таблице, то кнопку возможно нажать, иначе - нет"""
        self.ConfirmSelectionBtn.setEnabled(bool(self.GenresListWidget.selectedItems()))

    def set_genres(self):
        """Установка жанров при нажатии на кнопку и закрытие самого диалогового окна"""

        self.parent.set_genres(self.get_selected_genres(), self.tab)
        self.close()

    def get_selected_genres(self) -> list:
        """ Возвращает список с выбранными жанрами в виде их id в БД"""
        selected_genres = []
        for genre in map(lambda i: i.text(), self.GenresListWidget.selectedItems()):
            try:
                selected_genres.append(self.cur.execute("""SELECT genre_id FROM Genres WHERE title = ?""",
                                                        (genre,)).fetchone()[0])
            except TypeError:
                continue

        return selected_genres

    def closeEvent(self, event):
        self.db.close()
