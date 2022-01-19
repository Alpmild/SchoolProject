import sqlite3 as sql
# from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5 import uic

from Classes.Consts import (FSW_FILMS_TABLE_COLS_COUNT, FSW_FILMS_TABLE_COLS_SIZE, FSW_FILMS_TABLE_TITLES,
                            FSW_GENRES_TABLE_COLS_COUNT, FSW_GENRES_TABLE_COLS_SIZE, FSW_GENRES_TABLE_TITLES,
                            FSW_DIRECTORS_TABLE_COLS_COUNT, FSW_DIRECTORS_TABLE_COLS_SIZE, FSW_DIRECTORS_TABLE_TITLES,
                            FSW_SESSIONS_TABLE_COLS_COUNT, FSW_SESSIONS_TABLE_COLS_SIZE, FSW_SESSIONS_TABLE_TITLES)

from Classes.Communicate import Communicate


class FilmSelectionWindow(QMainWindow):
    """Класс для выбор фильма. Для дальнейшего его изменения в основном окне"""

    def __init__(self):
        super().__init__()
        self.current_film = 0

        self.com = Communicate()

        self.projectDB = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.projectDB_cur = self.projectDB.cursor()

        self.films_info = list(map(lambda i: dict(zip(FSW_FILMS_TABLE_TITLES, i)),
                                   self.projectDB_cur.execute("SELECT * FROM Films").fetchall()))
        for dict_ in self.films_info:
            film_id = dict_["film_id"]

            genres_req = f'SELECT genre_id FROM Films_Genres WHERE film_id = {film_id}'
            film_genres = list(map(lambda i: i[0], self.projectDB_cur.execute(genres_req).fetchall()))

            directors_req = f'SELECT director_id, name, surname FROM Films_Directors WHERE film_id = {film_id}'
            film_directors = self.projectDB_cur.execute(directors_req).fetchall()

            dict_['genres'], dict_['directors'] = film_genres, film_directors

        uic.loadUi('Interfaces\\FilmSelectionWindow.ui', self)
        self.init_ui()
        self.load_films_table()

    def init_ui(self):
        # Инициализация таблицы FilmsTable
        self.FilmsTable.setColumnCount(FSW_FILMS_TABLE_COLS_COUNT)
        self.FilmsTable.setHorizontalHeaderLabels(FSW_FILMS_TABLE_TITLES)

        for col, size in enumerate(FSW_FILMS_TABLE_COLS_SIZE):
            if isinstance(size, QHeaderView.ResizeMode):
                self.FilmsTable.horizontalHeader().setSectionResizeMode(col, size)
            else:
                self.FilmsTable.setColumnWidth(col, size)
                self.FilmsTable.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        # Инициализация таблицы GenresTable
        self.GenresTable.setColumnCount(FSW_GENRES_TABLE_COLS_COUNT)
        self.GenresTable.setHorizontalHeaderLabels(FSW_GENRES_TABLE_TITLES)

        for col, size in enumerate(FSW_GENRES_TABLE_COLS_SIZE):
            if isinstance(size, QHeaderView.ResizeMode):
                self.GenresTable.horizontalHeader().setSectionResizeMode(col, size)
            else:
                self.GenresTable.setColumnWidth(col, size)
                self.GenresTable.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        # Инициализация таблицы GenresTable
        self.DirectorsTable.setColumnCount(FSW_DIRECTORS_TABLE_COLS_COUNT)
        self.DirectorsTable.setHorizontalHeaderLabels(FSW_DIRECTORS_TABLE_TITLES)

        for col, size in enumerate(FSW_DIRECTORS_TABLE_COLS_SIZE):
            if isinstance(size, QHeaderView.ResizeMode):
                self.DirectorsTable.horizontalHeader().setSectionResizeMode(col, size)
            else:
                self.DirectorsTable.setColumnWidth(col, size)
                self.DirectorsTable.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        # Инициализация таблицы DirectorsTable
        self.SessionsTable.setColumnCount(FSW_SESSIONS_TABLE_COLS_COUNT)
        self.SessionsTable.setHorizontalHeaderLabels(FSW_SESSIONS_TABLE_TITLES)

        for col, size in enumerate(FSW_SESSIONS_TABLE_COLS_SIZE):
            if isinstance(size, QHeaderView.ResizeMode):
                self.SessionsTable.horizontalHeader().setSectionResizeMode(col, size)
            else:
                self.SessionsTable.setColumnWidth(col, size)
                self.SessionsTable.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        self.FilmsTable.cellClicked.connect(self.load_secondary_tables)

        self.SelectBtn.clicked.connect(self.radiate_signal)
        self.CancelBtn.clicked.connect(self.close)

    def load_films_table(self):
        """Загрузка всей основной информации в таблицу FilmsTable о фильмах из бд-таблицы Films"""
        self.FilmsTable.setRowCount(len(self.films_info))

        for row, film in enumerate(self.films_info):
            for col, title in enumerate(FSW_FILMS_TABLE_TITLES):
                item = QTableWidgetItem(str(self.films_info[row][title]))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.FilmsTable.setItem(row, col, item)

    def load_secondary_tables(self, r: int):
        if r < 0:
            return
        self.load_genres_table(r)
        self.load_directors_table(r)

    def load_genres_table(self, r: int):
        """Загрузка жанров выбранного фильма в таблицу GenresTable"""
        genres = self.films_info[r]['genres']
        self.GenresTable.clearContents()
        self.GenresTable.setRowCount(len(genres))

        for row, genre_id in enumerate(genres):
            str_genre = self.projectDB_cur.execute(
                f"SELECT title FROM Genres WHERE genre_id = {genre_id}").fetchone()[0]

            for col, elem in enumerate([QTableWidgetItem(str(genre_id)), QTableWidgetItem(str_genre)]):
                elem.setFlags(elem.flags() ^ Qt.ItemIsEditable)
                self.GenresTable.setItem(row, col, elem)

    def load_directors_table(self, r: int):
        """Загрузка режиссеров выбранного фильма в таблицу DirectorsTable"""
        pass

    def load_sessions_table(self, r: int):
        """Загрузка сеансов выбранного фильма в таблицу SessionsTable"""
        pass

    def radiate_signal(self):
        ind = self.FilmsTable.currentRow()
        if ind < 0:
            return
        self.current_film = self.films_info[ind]
        self.com.signal.emit()
