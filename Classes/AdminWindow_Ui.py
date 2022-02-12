from datetime import datetime, date, timedelta, time
import os
import os.path as os_path
from PIL import Image
from pprint import pprint

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QTabWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from Classes.Consts import *
from Classes.DirectorsSetupWindow_Ui import DirectorSetupDialog
from Classes.FilmSelectionWindow_Ui import FilmSelectionDialog
from Classes.GenreSelectionDialog_Ui import GenresSelectionDialog
from Classes.SessionSetupWindow_Ui import SessionSetupDialog
from Classes.Secondary_functions import transcription_name_into_english

import sqlite3 as sql


class AdminWindow(QTabWidget):
    """Основное окно админа, где можно добавлять, изменять и удалять фильмы"""

    def __init__(self):
        super().__init__()
        self.film_info_tab0, self.film_info_tab1 = FILM_INFO_TAB0.copy(), FILM_INFO_TAB1.copy()
        self.image_path_tab0, self.image_path_tab1 = '', ''
        self.genres_tab0, self.genres_tab1 = [], []
        self.directors_tab0, self.directors_tab1 = [], []
        self.sessions_tab0, self.sessions_tab1 = dict(), dict()

        self.tab1_editable = False

        self.projectDB = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.projectDB_cur = self.projectDB.cursor()

        uic.loadUi('Interfaces\\AdminWindow.ui', self)
        date_tab0 = self.CalendarTab0.selectedDate()
        date_tab1 = self.CalendarTab1.selectedDate()

        self.LinesTab0 = (self.CountryLineTab0, self.NameLineTab0)
        self.PlainTextsTab0 = (self.DescriptionPlainTextTab0,)
        self.SpinBoxesTab0 = (self.AgeRatingSpinBoxTab0, self.DurationSpinBoxTab0)
        self.selected_date_tab0 = date(date_tab0.year(), date_tab0.month(), date_tab0.day())

        self.LinesTab1 = (self.CountryLineTab1, self.NameLineTab1)
        self.PlainTextsTab1 = (self.DescriptionPlainTextTab1,)
        self.SpinBoxesTab1 = (self.AgeRatingSpinBoxTab1, self.DurationSpinBoxTab1)
        self.selected_date_tab1 = date(date_tab1.year(), date_tab1.month(), date_tab1.day())

        self.init_ui()
        for tab in range(2):
            self.init_tab_ui(tab)
        self.init_tab2_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.LoadFilmBtnTab1.clicked.connect(self.open_film_selection_window)
        self.CancelChangesBtnTab1.clicked.connect(lambda: self.clear_(1))
        self.set_tab1_edit()

    def init_tab_ui(self, tab: int):
        """Инициализация для вкладки tab"""
        ws = [
            [getattr(self, f'GenresTableTab{tab}'), AW_GENRES_TABLE_COLS_COUNT,
             AW_GENRES_TABLE_COLS_TITLES, AW_GENRES_TABLE_COLS_SIZE],
            [getattr(self, f'DirectorsTableTab{tab}'), AW_DIRECTORS_TABLE_COLS_COUNT,
             AW_DIRECTORS_TABLE_COLS_TITLES, AW_DIRECTORS_TABLE_COLS_SIZE],
            [getattr(self, f'SessionsTableTab{tab}'), AW_SESSIONS_TABLE_COLS_COUNT,
             AW_SESSIONS_TABLE_COLS_TITLES, AW_SESSIONS_TABLE_COLS_SIZE]
        ]
        for table, cols_count, titles, cols_size in ws:
            table.setColumnCount(cols_count)
            table.setHorizontalHeaderLabels(titles)
            for col, size in enumerate(cols_size):
                if isinstance(size, QHeaderView.ResizeMode):
                    table.horizontalHeader().setSectionResizeMode(col, size)
                else:
                    table.setColumnWidth(col, size)
                    table.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)

        getattr(self, f'GenresBtnTab{tab}').clicked.connect(lambda: self.open_genres_dialog(tab))

        getattr(self, f'AddDirectorBtnTab{tab}').clicked.connect(lambda: self.open_director_setup_dialog(tab))
        getattr(self, f'ChangeDirectorsBtnTab{tab}').clicked.connect(
            lambda: self.open_director_setup_dialog(tab, True))
        getattr(self, f'DeleteDirectorBtnTab{tab}').clicked.connect(lambda: self.delete_director(tab))

        getattr(self, f'AddSessionBtnTab{tab}').clicked.connect(
            lambda: self.open_session_setup_dialog(tab))
        getattr(self, f'ChangeSessionBtnTab{tab}').clicked.connect(
            lambda: self.open_session_setup_dialog(tab, True))
        getattr(self, f'DeleteSessionBtnTab{tab}').clicked.connect(
            lambda: self.delete_session(tab))

        getattr(self, f'LoadImageBtnTab{tab}').clicked.connect(lambda: self.load_image(tab))
        getattr(self, f'DeleteImageBtnTab{tab}').clicked.connect(lambda: self.delete_image(tab))

        getattr(self, f'ConfirmFilmInfoBtnTab{tab}').clicked.connect(lambda: self.confirm_info_press(tab))

        getattr(self, f'NameLineTab{tab}').textChanged.connect(
            lambda: self.set_value(tab, 'title', self.NameLineTab0.text()))
        getattr(self, f'CountryLineTab{tab}').textChanged.connect(
            lambda: self.set_value(tab, 'country', self.CountryLineTab0.text()))
        getattr(self, f'AgeRatingSpinBoxTab{tab}').valueChanged.connect(
            lambda: self.set_value(tab, 'rating', self.AgeRatingSpinBoxTab0.value()))
        getattr(self, f'DurationSpinBoxTab{tab}').valueChanged.connect(
            lambda: self.set_value(tab, 'duration', self.DurationSpinBoxTab0.value()))
        getattr(self, f'DescriptionPlainTextTab{tab}').textChanged.connect(
            lambda: self.set_value(tab, 'description', self.DescriptionPlainTextTab0.toPlainText()))

        now_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day) + timedelta(days=1)
        future_date = now_date + timedelta(days=30)

        sel_date = now_date + timedelta(days=1)

        calendar = getattr(self, f'CalendarTab{tab}')
        calendar.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        calendar.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        calendar.setSelectedDate(QDate(sel_date.year, sel_date.month, sel_date.day))
        calendar.selectionChanged.connect(lambda: (self.set_selected_date(tab), self.load_sessions_table(tab)))

        if tab == 0:
            self.selected_date_tab0 = sel_date.date()
        if tab == 1:
            self.selected_date_tab1 = sel_date.date()

    def init_tab2_ui(self):
        """
        Инициализация для вкладки Tab2
        """
        pass

    def set_value(self, tab: int, key, value):
        """
        Изменение цвета поля при введении текста
        """
        error_label = getattr(self, f'ErrorLabelTab{tab}')
        if self.sender().styleSheet() != NORMAL_LINE_COLOR:
            self.sender().setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')
        if error_label.styleSheet() != NORMAL_LINE_COLOR:
            error_label.clear()
            error_label.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')

        if isinstance(value, str):
            value = ' '.join(value.strip().split())

        getattr(self, f'film_info_tab{tab}')[key] = value

    def open_genres_dialog(self, tab: int):
        """
        Открытие диалога для выбора жанров
        """
        getattr(self, f'GenresTableTab{tab}').setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')

        if tab == 0 or (tab == 1 and self.tab1_editable):
            genres_dialog = GenresSelectionDialog(self, tab)
            genres_dialog.show()

    def set_genres(self, genres: list, tab: int):
        """Получение списка с жанрами"""

        getattr(self, f'film_info_tab{tab}')['genres'] = genres
        self.load_genres_table(tab)

    def load_genres_table(self, tab: int):
        genres_list = getattr(self, f'film_info_tab{tab}')['genres']
        genres_table = getattr(self, f'GenresTableTab{tab}')

        genres_table.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')
        genres_table.clearContents()
        genres_table.setRowCount(len(genres_list))

        for row, genre_id in enumerate(genres_list):
            items = (QTableWidgetItem(str(genre_id)), QTableWidgetItem(GENRES_DICT[genre_id]))
            for col, item in enumerate(items):
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                genres_table.setItem(row, col, item)

    def open_director_setup_dialog(self, tab: int, change=False):
        """
        Открыввется окно для добавления режиссера
        """
        table = getattr(self, f'DirectorsTableTab{tab}')
        table.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')

        if tab == 0 or (tab == 1 and self.tab1_editable):
            ind = table.currentRow()
            if change and ind != -1:
                name, surname = getattr(self, f'film_info_tab{tab}')['directors'][ind]
                self.director_dialog = DirectorSetupDialog(self, tab, ind, name, surname)
            else:
                self.director_dialog = DirectorSetupDialog(self, tab)

            table.setCurrentCell(-1, -1)
            self.director_dialog.show()

    def set_director(self, tab: int, ind: int, director: tuple):
        """
        Добавление режиссера в список, максимум self.MAX_DIRECTORS
        """
        director_list = getattr(self, f'film_info_tab{tab}')['directors']
        if ind != -1:
            director_list[ind] = director
        else:
            director_list.append(director)

        self.load_directors_table(tab)

    def delete_director(self, tab: int):
        """
        Удаление выбранного режиссёра, который человек выбирает в таблице DirectorsTableTab0
        """
        directors_list = getattr(self, f'film_info_tab{tab}')['directors']
        row = getattr(self, f'DirectorsTableTab{tab}').currentRow()

        if not directors_list or row == -1:
            return

        del directors_list[row]
        self.load_directors_table(tab)

    def load_directors_table(self, tab: int):
        """
        Загрузка таблицы с режиссёрами
        """
        directors_table = getattr(self, f'DirectorsTableTab{tab}')
        directors_list = getattr(self, f'film_info_tab{tab}')['directors']

        directors_table.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')
        directors_table.clearContents()
        directors_table.setRowCount(len(directors_list))

        for row, director in enumerate(directors_list):
            for col, name in enumerate(director):
                item = QTableWidgetItem(name)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                directors_table.setItem(row, col, item)

    def open_session_setup_dialog(self, tab: int, change=False):
        """
        Открытие окна, для добавления сеанса
        """
        selected_date = getattr(self, f'selected_date_tab{tab}')
        table = getattr(self, f'SessionsTableTab{tab}')

        sessions_error_label = getattr(self, f'SessionsErrorLabelTab{tab}')
        sessions_error_label.setText('')
        sessions_error_label.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')

        if tab == 0 or (tab == 1 and self.tab1_editable):
            row = table.currentRow()

            if change and row != -1:
                session = getattr(self, f'film_info_tab{tab}')['sessions'][selected_date][row]

                if len(session) == 3:
                    session_id, time_, hall = getattr(self, f'film_info_tab{tab}')['sessions'][selected_date][row]
                    self.session_dialog = SessionSetupDialog(self, tab, selected_date, time_, hall, row, session_id)
                else:
                    time_, hall = getattr(self, f'film_info_tab{tab}')['sessions'][selected_date][row]
                    self.session_dialog = SessionSetupDialog(self, tab, selected_date, time_, hall, row, -1)
            else:
                self.session_dialog = SessionSetupDialog(self, tab, selected_date)

            table.setCurrentCell(-1, -1)
            self.session_dialog.show()

    def set_session(self, tab: int, date_: date, time_: time, hall: int, index: int, session_id: int):
        """
        Добавление сенса в определенный день
        """
        sessions = getattr(self, f'film_info_tab{tab}')['sessions']
        if index == -1:
            if date_ not in sessions:
                sessions[date_] = []
            if session_id == -1:
                sessions[date_].append((time_, hall))
            else:
                sessions[date_].append((session_id, time_, hall))
        else:
            if session_id == -1:
                sessions[date_][index] = (time_, hall)
            else:
                sessions[date_][index] = (session_id, time_, hall)

        sessions[date_].sort(key=lambda x: x[0].minute)
        sessions[date_].sort(key=lambda x: x[0].hour)

        self.load_sessions_table(tab)

    def delete_session(self, tab: int):
        """
        Удаление выбранного сеанса, выбранного в таблице
        """
        table = getattr(self, f'SessionsTableTab{tab}')
        sessions = getattr(self, f'film_info_tab{tab}')['sessions']
        selected_date = getattr(self, f'selected_date_tab{tab}')

        ind = table.currentRow()
        if ind == -1:
            return

        ses = sessions[selected_date].pop(ind)
        try:
            deleted_sessions = getattr(self, f'film_info_tab{tab}')['deleted_sessions']
            if len(ses) == 3:
                deleted_sessions.append(ses[0])
        except KeyError:
            pass

        if not sessions[selected_date]:
            del sessions[selected_date]

        table.setCurrentCell(-1, -1)
        self.load_sessions_table(tab)

    def load_sessions_table(self, tab: int):
        """
        Загрузка сеансов, если они есть в определнггый день
        """
        attrs = ('SessionsTableTab{}', 'selected_date_tab{}', 'SessionsErrorLabelTab{}')
        sessions_table, selected_date, sessions_error_label = \
            map(lambda i: getattr(self, i.format(tab)), attrs)
        sessions = getattr(self, f'film_info_tab{tab}')['sessions']

        # Загрузка сеансов
        sessions_table.clearContents()
        sessions_table.setRowCount(0)

        if selected_date in sessions:
            sessions_table.setRowCount(len(sessions[selected_date]))
            sessions = sessions[selected_date]

            for row, ses in enumerate(sessions):
                if len(ses) == 3:
                    time_, hall = ses[1:]
                else:
                    time_, hall = ses
                session_info = [QTableWidgetItem(time_.strftime('%H:%M')), QTableWidgetItem(str(hall))]

                for col, elem in enumerate(session_info):
                    elem.setFlags(elem.flags() ^ Qt.ItemIsEditable)
                    sessions_table.setItem(row, col, elem)

        sessions_error_label.setText('')
        sessions_error_label.setStyleSheet(f'background-color: {NORMAL_WINDOW_COLOR}')

    def set_selected_date(self, tab: int):
        calendar = getattr(self, f'CalendarTab{tab}')
        selected_date = calendar.selectedDate()

        if tab == 0:
            self.selected_date_tab0 = date(selected_date.year(), selected_date.month(), selected_date.day())
        else:
            self.selected_date_tab1 = date(selected_date.year(), selected_date.month(), selected_date.day())

    def load_image(self, tab: int, path_to_image=''):
        """
        Получение изображения
        """
        error_label = getattr(self, f'ImageErrorLabelTab{tab}')
        error_label.clear()

        if not path_to_image and (tab == 0 or (tab == 1 and self.tab1_editable)):
            path_to_image = QFileDialog.getOpenFileName(  # Используется при сохранении фильма
                self, 'Выбрать картинку', '',
                'Изображение (*.jpg);;Изображение (*.jpeg);;Изображение (*.png)')[0]
            if not path_to_image:
                return

            path_to_image = path_to_image.replace('/', '\\')
            getattr(self, f'film_info_tab{tab}')['image_path'] = path_to_image

        print(path_to_image)

        image = QPixmap(path_to_image)
        image_label_width, image_label_height = (self.ImageLabelTab0.geometry().width(),
                                                 self.ImageLabelTab0.geometry().height())
        w, h = image.width(), image.height()

        if IMAGE_WIDTH / IMAGE_HEIGHT + 0.15 > w / h > IMAGE_WIDTH / IMAGE_HEIGHT - 0.15 \
                and h >= IMAGE_HEIGHT and w >= IMAGE_WIDTH:

            resized_image = image.scaled(image_label_width, image_label_height)
            getattr(self, f'ImageLabelTab{tab}').setPixmap(resized_image)
        else:
            error_label.setText('Изображение не подходит.\n'
                                'Соотношение сторон должно быть\n'
                                '7:10.')

    def delete_image(self, tab: int):
        """Удаление выбранного изображения"""
        getattr(self, f'film_info_tab{tab}')['image_path'] = ''
        getattr(self, f'ImageLabelTab{tab}').clear()

    def open_film_selection_window(self):
        """Открывается окно для выбора фильма на изменение"""
        film_selection_window = FilmSelectionDialog(self)
        film_selection_window.show()

    def load_film_tab1(self, film_info: dict):
        """Загрузка фильма в окне tab1"""
        self.tab1_editable = True
        self.film_info_tab1 = film_info
        title, country, description = film_info['title'], film_info['country'], film_info['description']

        self.set_tab1_edit()

        self.load_genres_table(1)
        self.load_directors_table(1)
        self.load_sessions_table(1)

        self.NameLineTab1.setText(film_info['title'])
        self.CountryLineTab1.setText(film_info['country'])
        self.DescriptionPlainTextTab1.setPlainText(film_info['description'])

        self.load_image(1, film_info['image_path'])

        film_info['title'], film_info['country'], film_info['description'] = title, country, description

    def set_tab1_edit(self):
        """Установка возможности редактированимя данных"""
        edit = not self.tab1_editable
        for field in self.LinesTab1 + self.SpinBoxesTab1 + self.PlainTextsTab1:
            field.setReadOnly(edit)

    def confirm_info_press(self, tab: int):
        """Подтвеждение введенной информации"""
        if self.info_verification(tab):
            self.filling_data(tab)
        else:
            self.specifying_invalid_fields(tab)

    def info_verification(self, tab: int):
        """Проверка данных"""
        film_info = getattr(self, f'film_info_tab{tab}')
        for key in FILMS_INFO_CHECKED_PARAMS:
            arg = film_info[key]
            if type(arg) in (dict, list, tuple) and not arg:
                return False

        if not (''.join(film_info['title'].split()).isalnum() and ''.join(film_info['country'].split()).isalpha()
                and film_info['description'] and film_info['image_path']):
            return False

        return os_path.exists(film_info['image_path'])

    def specifying_invalid_fields(self, tab: int):
        """Указание пустых или неправильно заполненных полей """
        film_info = getattr(self, f'film_info_tab{tab}')

        name_line = getattr(self, f'NameLineTab{tab}')
        country_line = getattr(self, f'CountryLineTab{tab}')
        genres_table = getattr(self, f'GenresTableTab{tab}')
        directors_table = getattr(self, f'DirectorsTableTab{tab}')
        description_plaintext = getattr(self, f'DescriptionPlainTextTab{tab}')
        sessions_error_label = getattr(self, f'SessionsErrorLabelTab{tab}')
        image_error_label = getattr(self, f'ImageErrorLabelTab{tab}')

        if not ''.join(film_info['title'].split()).isalnum():
            name_line.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not ''.join(film_info['country'].split()).isalpha():
            country_line.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not film_info['genres']:
            genres_table.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not film_info['directors']:
            directors_table.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not film_info['description']:
            description_plaintext.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not film_info['sessions']:
            sessions_error_label.setStyleSheet(f'background-color: {ERROR_COLOR}')
            sessions_error_label.setText('Добавте хотя бы 1 сеанс')

        if not os_path.exists(film_info['image_path']):
            self.delete_image(tab)
            getattr(self, f'ImageLabelTab{tab}').clear()

        if not film_info['image_path']:
            image_error_label.setText('Выберите постера фильма в\n'
                                      'примерном соотношении сторон 7:10')

    def filling_data(self, tab: int):
        """Запись основной информации в базу данных"""
        film_info = getattr(self, f'film_info_tab{tab}')

        title, country, rating, duration, image_path = \
            (film_info['title'], film_info['country'], film_info['rating'],
             film_info['duration'], film_info['image_path'])

        file_folder_name = transcription_name_into_english(film_info['title'])
        description_file_name, image_name = (f'Films\\{file_folder_name}\\{file_folder_name}Description.txt',
                                             f'Films\\{file_folder_name}\\{file_folder_name}Image.png')

        if tab == 0:

            if (file_folder_name,) in self.projectDB_cur.execute('SELECT file_folder_name FROM Films').fetchall():
                self.ErrorLabelTab0.setText('Этот фильм уже есть в базе.')
                self.ErrorLabelTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')
                return

            # Создание папки
            os.mkdir(f'Films\\{file_folder_name}')

            # Запись описания в текстовый файл
            with open(description_file_name, 'w') as description_file:
                description_file.write(film_info['description'])

            # Сохранение постера фильма
            image = Image.open(image_path)
            new_image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
            new_image.save(image_name)

            # Запись информации в бд
            self.projectDB_cur.execute(
                "INSERT INTO "
                "Films(title, country, rating, duration, file_folder_name, description_file_name, image_name) "
                "VALUES(?, ?, ?, ?, ?, ?, ?)",
                (title, country, rating, duration, file_folder_name, description_file_name, image_name))

            self.projectDB.commit()

            film_id = self.projectDB_cur.execute("SELECT film_id FROM Films"
                                                 "    WHERE file_folder_name = ?", (file_folder_name,)).fetchone()[0]

            genres, directors, sessions = film_info['genres'], film_info['directors'], film_info['sessions']

            self.filling_genres(film_id, genres, tab)
            self.filling_directors(film_id, directors, tab)
            self.filling_sessions(film_id, sessions, [])
            self.clear_(tab)

        elif tab == 1:
            film_id = film_info['film_id']

            last_file_folder_name, last_description_file_name, last_image_name = \
                self.projectDB_cur.execute(
                    "SELECT file_folder_name, description_file_name, image_name FROM Films"
                    "    WHERE film_id = ?",
                    (film_id,)).fetchone()

            # Запись описания в текстовый файл
            if file_folder_name != last_file_folder_name:
                os.rename(last_description_file_name, description_file_name)
            with open(description_file_name, 'w') as description_file:
                description_file.write(film_info['description'])

            # Сохранение изображения
            if image_path in (last_image_name, f'{os.getcwd()}\\{last_image_name}'):
                os.rename(image_path, image_name)
            else:
                image = Image.open(image_path)
                new_image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
                new_image.save(f'Films\\{last_file_folder_name}\\{file_folder_name}Image.png')

            if last_file_folder_name != file_folder_name:
                os.rename(last_file_folder_name, file_folder_name)

            self.projectDB_cur.execute("UPDATE FILMS"
                                       "SET title = ?,"
                                       "    country = ?,"
                                       "    rating = ?,"
                                       "    duration = ?,"
                                       "    file_folder_name = ?,"
                                       "    description_file_name = ?,"
                                       "    image_name = ?"
                                       "WHERE"
                                       "    film_id = ?",
                                       (title, country, rating, duration, file_folder_name,
                                        description_file_name, image_name, film_id))
            self.projectDB.commit()

    def filling_genres(self, film_id: int, genres: list, tab: int):
        """Запись жанров фильма в таблицу Films_Genres."""
        if tab == 1:
            self.projectDB_cur.execute("DELETE FROM Films_Genres WHERE film_id = ?", (film_id,))

        for genre_id in genres:
            self.projectDB_cur.execute("INSERT INTO Films_Genres VALUES (?, ?)", (film_id, genre_id))
            self.projectDB.commit()

    def filling_directors(self, film_id: int, directors: list, tab: int):
        """Запись режиссеров фильма в таблицу Films_Directors"""
        if tab == 1:
            self.projectDB_cur.execute("DELETE FROM Films_Directors WHERE film_id = ?", (film_id,))
            self.projectDB.commit()

        for name, surname in directors:
            self.projectDB_cur.execute("INSERT INTO Films_Directors VALUES(?, ?, ?)", (film_id, name, surname))
            self.projectDB.commit()

    def filling_sessions(self, film_id: int, sessions: dict, del_sessions: list):
        """Запись сеансов в таблицу Sessions"""
        for ses_id in del_sessions:
            self.projectDB_cur.execute("DELETE FROM Sessions WHERE session_id = ?", (ses_id,))

        for date_ in sessions:
            year, month, day = date_.year, date_.month, date_.day

            for ses in sessions[date_]:
                if len(ses) == 3:
                    ses_id, time_, hall = ses
                    hour, minute = time_.hour, time_.minute

                    self.projectDB_cur.execute("INSERT INTO Sessions VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                                               (film_id, ses_id, year, month, day, hour, minute, hall))
                else:
                    time_, hall = ses
                    hour, minute = time_.hour, time_.minute

                    self.projectDB_cur.execute("INSERT INTO Sessions(film_id, year, month, day, hour, minute, hall_id) "
                                               "VALUES(?, ?, ?, ?, ?, ?, ?)",
                                               (film_id, year, month, day, hour, minute, hall))
                self.projectDB.commit()

    def clear_(self, tab: int):
        """Очистка всей информации о фильме, записанная внутри класса, и всех полей"""
        if tab == 0:
            film_info = self.film_info_tab0 = FILM_INFO_TAB0.copy()
        if tab == 1:
            film_info = self.film_info_tab1 = FILM_INFO_TAB1.copy()
        film_info['directors'], film_info['sessions'] = list(), dict()

        for field in getattr(self, f'LinesTab{tab}') + getattr(self, f'PlainTextsTab{tab}'):
            field.clear()

        getattr(self, f'AgeRatingSpinBoxTab{tab}').setValue(MIN_AGE_RATING)
        getattr(self, f'DurationSpinBoxTab{tab}').setValue(MIN_DURATION)

        error_label = getattr(self, f'ErrorLabelTab{tab}')
        error_label.clear()
        error_label.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')

        self.load_genres_table(tab)
        self.load_directors_table(tab)
        self.load_sessions_table(tab)

        self.delete_image(tab)

        if tab == 1:
            self.tab1_editable = False
            self.set_tab1_edit()

    def closeEvent(self, event):
        self.projectDB.close()
