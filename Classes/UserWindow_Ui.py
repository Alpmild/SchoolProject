import sqlite3 as sql
from datetime import datetime, date, timedelta, time

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView
from PyQt5 import uic

from Classes.Consts import UW_FILMS_TABLE_TITLES, UW_FILMS_TABLE_COLS_COUNT, UW_FILMS_TABLE_COLS_SIZE
from Classes.FilmWindow_Ui import FilmWindow


class UserWindow(QMainWindow):
    """
    Основное окно пользователя
    """
    def __init__(self):
        super().__init__()
        self.films_current_date = []

        uic.loadUi('Interfaces\\UserWindow.ui', self)
        self.projectDB = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.projectDB_cur = self.projectDB.cursor()
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Выбор фильма')

        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.Calendar.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.Calendar.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        self.Calendar.selectionChanged.connect(self.load_table_films)

        self.FilmsTable.setColumnCount(UW_FILMS_TABLE_COLS_COUNT)
        self.FilmsTable.setHorizontalHeaderLabels(UW_FILMS_TABLE_TITLES)

        for col, size in enumerate(UW_FILMS_TABLE_COLS_SIZE):
            print(type(size))
            if isinstance(size, QHeaderView.ResizeMode):
                self.FilmsTable.horizontalHeader().setSectionResizeMode(col, size)
            else:
                self.FilmsTable.setColumnWidth(col, size)
                self.FilmsTable.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        self.FilmsTable.cellDoubleClicked.connect(self.open_film_window)
        self.load_table_films()

    def load_table_films(self) -> None:
        """
        Загрузка таблицы в зависимости от даты
        """
        self.FilmsTable.clearContents()
        films_data = self.get_films_by_date()

        self.FilmsTable.setRowCount(len(films_data))

        for row_ind, row in enumerate(films_data):  # Добаввление дынных в таблицу
            title, rating, duration, genres = row
            genres = ', '.join(genres).capitalize()

            hours_dur, minutes_dur = divmod(duration, 60)
            if hours_dur > 0 and minutes_dur > 0:
                duration = f'{hours_dur}ч {minutes_dur}мин.'
            elif hours_dur > 0 and minutes_dur == 0:
                duration = f'{hours_dur}ч'
            else:
                duration = f'{minutes_dur}мин.'

            film_info = [title, genres, f'{rating}+', duration]
            for column_ind, element in enumerate(film_info):
                item = QTableWidgetItem(element)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.FilmsTable.setItem(row_ind, column_ind, item)

    def get_films_by_date(self) -> list:
        """
        Возвращение списка с фильмами и нужной инфой, который показывают в выбранную дату
        """
        self.films_current_date.clear()
        suitable_films = []

        now_date = datetime.now().date()
        now_time = (datetime.now() + timedelta(minutes=15)).time()

        selected_date = (self.Calendar.selectedDate().year(), self.Calendar.selectedDate().month(),
                         self.Calendar.selectedDate().day())

        films_ids = sorted(list(set(map(lambda x: x[0], set(self.projectDB_cur.execute(
            "SELECT film_id FROM Sessions WHERE year = ? AND month = ? AND day = ?", selected_date).fetchall())))))

        for film_id in films_ids:
            sessions = self.projectDB_cur.execute(
                "SELECT session_id, hour, minute, hall_id FROM Sessions "
                "WHERE year = ? AND month = ? AND day = ? AND film_id = ?", (*selected_date, film_id)).fetchall()

            if date(*selected_date) == now_date:
                sessions = sorted(tuple(filter(lambda x: now_time < time(x[1], x[2]), sessions)))

            if not sessions:
                continue

            genres = map(lambda x: x[0], self.projectDB_cur.execute(
                "SELECT genre_id FROM Films_Genres WHERE film_id = ?", (film_id,)).fetchall())
            genres = tuple(map(lambda x: self.projectDB_cur.execute(
                "SELECT title FROM Genres WHERE genre_id = ?", (x,)).fetchone()[0], genres))

            directors = tuple(self.projectDB_cur.execute(
                "SELECT name, surname FROM Films_Directors WHERE film_id = ?", (film_id,)).fetchall())

            all_film_info = self.projectDB_cur.execute(
                "SELECT * FROM Films WHERE film_id = ?", (film_id,)).fetchone()
            lite_film_info = self.projectDB_cur.execute(
                "SELECT title, rating, duration FROM Films WHERE film_id = ?", (film_id,)).fetchone()

            self.films_current_date.append((all_film_info, genres, directors, sessions))
            suitable_films.append((*lite_film_info, genres))

        if self.films_current_date:
            self.films_current_date.sort(key=lambda x: x[0][1])
        if suitable_films:
            suitable_films.sort(key=lambda x: x[0])
        return suitable_films

    def open_film_window(self, row_ind: int) -> None:
        """
        Открытия окна фильма со всей информацией
        """
        self.filmWindow = FilmWindow(*self.films_current_date[row_ind])
        self.filmWindow.show()

    def closeEvent(self, event):
        if hasattr(self, 'filmWindow'):
            self.filmWindow.close()
        self.projectDB.close()
        self.close()
