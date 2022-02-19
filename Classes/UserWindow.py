from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QTableWidgetItem, QMainWindow
from PyQt5 import uic

from Classes.Consts import *
from Classes.FilmWindow import FilmWindow
from Classes.GenresSelectionDialog import GenresSelectionDialog

from datetime import date, time, datetime
import sqlite3 as sql
from pprint import pprint

from PyQt5.QtWidgets import QHeaderView


class UserWindow(QMainWindow):
    """
    Основное окно пользователя
    """

    def __init__(self):
        super().__init__()
        self.FilmWindow = None
        self.GenresDialog = GenresSelectionDialog(self, 0, True)

        self.films, self.right_films = [], []

        uic.loadUi(UW_INTERFACE, self)
        self.projectDB = sql.connect(PROJECT_DATABASE)
        self.projectDB_cur = self.projectDB.cursor()

        self.search_info = UW_SEARCH_INFO.copy()

        for film_info in self.projectDB_cur.execute("SELECT * FROM Films").fetchall():
            film_info = dict(zip(FILMS_TABLE_KEYS, film_info))
            film_id = film_info['film_id']

            sessions = self.projectDB_cur.execute(
                "SELECT year, month, day, session_id, hour, minute, hall_id FROM Sessions"
                "   WHERE film_id = ?", (film_id,)).fetchall()

            sessions_dict = dict()
            for ses in sessions:
                date_ = date(*ses[:3])
                info = (ses[3], time(*ses[4:6]), ses[6])

                if date_ == MIN_DATE:
                    if info[1] >= (datetime.now() - timedelta(minutes=15)).time():
                        if date_ not in sessions_dict:
                            sessions_dict[date_] = []
                        sessions_dict[date_].append(info)

                elif date_ > MIN_DATE:
                    if date_ not in sessions_dict:
                        sessions_dict[date_] = []
                    sessions_dict[date_].append(info)
                else:
                    continue

            if not sessions_dict:
                continue

            film_info['sessions'] = sessions_dict

            film_info['genres'] = tuple(map(lambda i: i[0], self.projectDB_cur.execute(
                "SELECT genre_id FROM Films_Genres WHERE film_id = ?", (film_id,)).fetchall()))

            film_info['directors'] = self.projectDB_cur.execute(
                "SELECT name, surname FROM Films_Directors WHERE film_id = ?", (film_id,)).fetchall()

            self.films.append(film_info)

        self.init_ui()
        self.load_films_table()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setWindowTitle('Выбор фильма')

        self.Calendar.clicked.connect(self.set_date)
        self.NameLine.textChanged.connect(self.set_name)
        self.IndicateGenresBtn.clicked.connect(self.GenresDialog.show)
        self.StartRatingSpinBox.valueChanged.connect(lambda value: self.set_rating(value, 0))
        self.EndRatingSpinBox.valueChanged.connect(lambda value: self.set_rating(value, 1))

        self.Calendar.setMinimumDate(QDate(MIN_DATE.year, MIN_DATE.month, MIN_DATE.day))
        self.Calendar.setMaximumDate(QDate(MAX_DATE.year, MAX_DATE.month, MAX_DATE.day))

        self.StartRatingSpinBox.setRange(MIN_AGE_RATING, MAX_AGE_RATING)
        self.EndRatingSpinBox.setRange(MIN_AGE_RATING, MAX_AGE_RATING)
        self.EndRatingSpinBox.setValue(MAX_AGE_RATING)

        self.FilmsTable.setColumnCount(UW_FILMS_TABLE_COLS_COUNT)
        self.FilmsTable.setHorizontalHeaderLabels(UW_FILMS_TABLE_TITLES)

        for col, size in enumerate(UW_FILMS_TABLE_COLS_SIZE):
            if isinstance(size, QHeaderView.ResizeMode):
                self.FilmsTable.horizontalHeader().setSectionResizeMode(col, size)
            else:
                self.FilmsTable.setColumnWidth(col, size)
                self.FilmsTable.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        self.FilmsTable.cellDoubleClicked.connect(self.open_film_window)
        self.load_films_table()

    def load_films_table(self):
        """Загрузка таблицы в зависимости от даты"""
        self.set_right_films()
        pprint(self.search_info)
        pprint(self.right_films)

        self.FilmsTable.clearContents()
        self.FilmsTable.setRowCount(len(self.right_films))

        for row, film_info in enumerate(self.right_films):
            genres = ', '.join(map(lambda genre_id: GENRES_DICT[genre_id], film_info['genres'])).capitalize()
            h, m = divmod(film_info['duration'], 60)
            if h > 0 and m > 0:
                duration = f'{h}ч. {m}мин.'
            elif h > 0 and m == 0:
                duration = f'{h}ч.'
            else:
                duration = f'{m}мин.'

            info = (film_info['title'], film_info['country'], genres, str(film_info['rating']), duration)

            for col, elem in enumerate(info):
                item = QTableWidgetItem(elem)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.FilmsTable.setItem(row, col, item)

    def set_right_films(self):
        """Установка списка с фильмами по выбранной дате"""

        date_ = self.search_info['date']
        self.right_films = filter(lambda film: date_ in film['sessions'], self.films)
        if date_ == MIN_DATE:
            now_time = (datetime.now() + timedelta(minutes=15)).time()

            self.right_films = filter(
                lambda film_info: any(ses[1] >= now_time for ses in film_info['sessions'][date_]), self.right_films)

        if self.search_info['title']:
            title = self.search_info['title']
            self.right_films = filter(
                lambda film_info: (title in ''.join(film_info['title'].split()).lower()
                                   or title in film_info['title'].lower()),
                self.right_films)

        if self.search_info['genres']:
            genres = self.search_info['genres']
            self.right_films = filter(
                lambda film_info: all(map(lambda genre: genre in film_info['genres'], genres)), self.right_films)

        start, end = self.search_info['rating']
        self.right_films = filter(lambda film_info: start <= film_info['rating'] <= end, self.right_films)

        self.right_films = list(self.right_films)
        self.right_films.sort(key=lambda i: i['title'])

    def set_date(self, date_: QDate):
        """Запись даты, по которой будут фильтроваться филмы из базы"""
        self.search_info['date'] = date(date_.year(), date_.month(), date_.day())
        self.load_films_table()

    def set_name(self, name: str):
        """Запись названия, по которому будут фильтроваться филмы из базы"""
        self.search_info['title'] = ' '.join(name.lower().split())
        self.load_films_table()

    def set_genres(self, genres: list, tab: int):
        """Запись жанров, по которым будут фильтроваться филмы из базы"""
        assert tab == 0
        self.search_info['genres'] = genres
        self.GenresLine.setText(', '.join(map(lambda genre: GENRES_DICT[genre], genres)).capitalize())
        self.load_films_table()

    def set_rating(self, rating: int, ind: int):
        """Запись возростного рейтинга, по которой будут фильтроваться филмы из базы"""
        if ind == 0:
            self.EndRatingSpinBox.setMinimum(rating)
        self.search_info['rating'][ind] = rating
        self.load_films_table()

    def open_film_window(self, row_ind: int):
        """Открытия окна фильма со всей информацией"""
        date_ = self.Calendar.selectedDate()
        date_ = date(date_.year(), date_.month(), date_.day())

        self.FilmWindow = FilmWindow(self.right_films[row_ind], date_)
        self.FilmWindow.show()

    def closeEvent(self, event):
        try:
            self.FilmWindow.close()
        except AttributeError:
            pass
        self.projectDB.close()
