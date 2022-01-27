import sqlite3 as sql
from datetime import datetime, date, timedelta, time
import os
import os.path
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


class AdminWindow(QTabWidget):
    """Основное окно админа, где можно добавлять, изменять и удалять фильмы"""
    film_info_tab0 = {"film_id": None, "title": "", "country": "", "genres": [], "rating": 0,
                      "duration": 30, "description": "", "sessions": dict(), "image_path": ""}

    film_info_tab1 = {"film_id": None, "title": "", "country": "", "genres": [], "rating": 0,
                      "duration": 30, "description": "", "sessions": dict(),
                      "file_folder_name": "", "description_file_name": "", "image_path": ""}

    def __init__(self):
        super().__init__()
        self.ERROR_COLOR = '#ff5133'
        self.NORMAL_COLOR = '#ffffff'

        self.image_path_tab0 = ''
        self.genres_tab0 = []
        self.directors_tab0 = []
        self.sessions_tab0 = {}

        self.image_path_tab1 = ''
        self.genres_tab1 = []
        self.directors_tab1 = []
        self.sessions_tab1 = {}

        self.projectDB = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.projectDB_cur = self.projectDB.cursor()

        uic.loadUi('Interfaces\\AdminWindow.ui', self)
        date_tab0 = self.CalendarTab0.selectedDate()
        date_tab1 = self.CalendarTab1.selectedDate()

        self.LinesTab0 = (self.CountryLineTab0, self.NameLineTab0, self.GenresLineTab0)
        self.PlainTextsTab0 = (self.DescriptionPlainTextTab0,)
        self.SpinBoxesTab0 = (self.AgeRatingSpinBoxTab0, self.DurationSpinBoxTab0)
        self.selected_date_tab0 = date(date_tab0.year(), date_tab0.month(), date_tab0.day())

        self.LinesTab1 = (self.CountryLineTab1, self.NameLineTab1, self.GenresLineTab1)
        self.PlainTextsTab1 = (self.DescriptionPlainTextTab1,)
        self.SpinBoxesTab1 = (self.AgeRatingSpinBoxTab1, self.DurationSpinBoxTab1)
        self.selected_date_tab1 = date(date_tab1.year(), date_tab1.month(), date_tab1.day())

        self.setFixedSize(self.size())
        self.init_tab0_ui()
        self.init_tab1_ui()
        self.init_tab2_ui()

    def init_tab0_ui(self):
        """Инициализация для вкладки Tab0"""

        self.GenresBtnTab0.clicked.connect(lambda: self.open_genres_dialog(0))

        self.DirectorsTableTab0.setHorizontalHeaderLabels(["Имя", "Фамилия"])
        for i in range(self.DirectorsTableTab0.columnCount()):
            self.DirectorsTableTab0.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.AddDirectorBtnTab0.clicked.connect(lambda: self.open_director_setup_dialog(0))
        self.ChangeDirectorsBtnTab0.clicked.connect(lambda: self.open_director_setup_dialog(0, True))
        self.DeleteDirectorBtnTab0.clicked.connect(lambda: self.delete_director(0))

        for field in self.LinesTab0 + self.PlainTextsTab0:
            field.textChanged.connect(lambda: self.set_line_text_back_color(0))

        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.CalendarTab0.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.CalendarTab0.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        self.CalendarTab0.selectionChanged.connect(lambda: (self.set_selected_date(0), self.load_sessions_table(0)))

        self.AddSessionBtnTab0.clicked.connect(lambda: self.open_session_setup_dialog(0))
        self.ChangeSessionBtnTab0.clicked.connect(lambda: self.open_session_setup_dialog(0, True))
        self.DeleteSessionBtnTab0.clicked.connect(lambda: self.delete_session(0))

        self.SessionsTableTab0.setHorizontalHeaderLabels(["Время", "Зал"])
        for i in range(self.SessionsTableTab0.columnCount()):
            self.SessionsTableTab0.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.LoadImageBtnTab0.clicked.connect(self.load_image)
        self.DeleteImageBtnTab0.clicked.connect(self.delete_image)

        self.ConfirmFilmInfoBtnTab0.clicked.connect(self.confirm_info_press)

    def init_tab1_ui(self):
        """
        Инициализация для вкладки Tab1
        """
        #  self.GenresBtnTab1.clicked.connect()

        self.DirectorsTableTab1.setHorizontalHeaderLabels(["Имя", "Фамилия"])
        for i in range(self.DirectorsTableTab1.columnCount()):
            self.DirectorsTableTab1.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        #  self.AddDirectorBtnTab1.clicked.connect()
        #  self.ChangeDirectorsBtnTab1.clicked.connect()
        #  self.DeleteDirectorBtnTab1.clicked.connect()

        # for field in self.LinesTab1 + self.PlainTextsTab1:
        #     field.textChanged.connect(self.set_line_text_back_color)

        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.CalendarTab1.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.CalendarTab1.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        # self.CalendarTab1.selectionChanged.connect(self.load_sessions_table)

        self.SessionsTableTab1.setHorizontalHeaderLabels(["Время", "Зал"])
        for i in range(self.SessionsTableTab1.columnCount()):
            self.SessionsTableTab1.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        #  self.LoadImageBtnTab1.clicked.connect()
        #  self.DeleteImageBtnTab1.clicked.connect()

        self.LoadFilmBtnTab1.clicked.connect(self.open_film_selection_window)

        #  self.ConfirmFilmInfoBtnTab1.clicked.connect()

    def init_tab2_ui(self):
        """
        Инициализация для вкладки Tab2
        """
        pass

    def set_line_text_back_color(self, tab: int):
        """
        Изменение цвета поля при введении текста
        """
        error_label = getattr(self, f'ErrorLabelTab{tab}')
        if self.sender().styleSheet() != NORMAL_LINE_COLOR:
            self.sender().setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')
        if error_label.styleSheet() != NORMAL_LINE_COLOR:
            error_label.clear()

    def open_film_selection_window(self):
        """Открывается окно для выбора фильма на изменение"""
        film_selection_window = FilmSelectionDialog(self)
        film_selection_window.show()

    def set_film_tab1(self):
        pass

    def open_genres_dialog(self, tab: int):
        """
        Открытие диалога для выбора жанров
        """
        genres_dialog = GenresSelectionDialog(self, tab)
        genres_dialog.show()

    def set_genres(self, genres: list, tab: int):
        """Получение списка с жанрами"""

        if tab == 0:
            self.genres_tab0 = genres
        elif tab == 1:
            self.genres_tab1 = genres
        else:
            raise IndexError('Индекс вкладки не соответсвет индексации')
        str_genres = []

        for genre_id in self.genres_tab0:
            try:
                str_genres.append(str(self.projectDB_cur.execute("""SELECT title FROM Genres WHERE genre_id = ?""",
                                                                 (genre_id,)).fetchone()[0]))
            except TypeError:
                continue

        getattr(self, f'GenresLineTab{tab}').setText(', '.join(str_genres).capitalize())
        str_genres.clear()

    def open_director_setup_dialog(self, tab: int, change=False):
        """
        Открыввется окно для добавления режиссера
        """
        table = getattr(self, f'DirectorsTableTab{tab}')
        if change:
            ind = table.currentRow()
            if ind == -1:
                return
            name, surname = getattr(self, f'directors_tab{tab}')[ind]
            self.director_dialog = DirectorSetupDialog(self, tab, ind, name, surname)
        else:
            self.director_dialog = DirectorSetupDialog(self, tab)

        table.setCurrentCell(-1, -1)
        self.director_dialog.show()

    def set_director(self, tab: int, ind: int, director: tuple):
        """
        Добавление режиссера в список, максимум self.MAX_DIRECTORS
        """
        directors_list = getattr(self, f'directors_tab{tab}')
        if ind != -1:
            directors_list[ind] = director
        else:
            directors_list.append(director)

        self.load_directors_table(tab)

    def delete_director(self, tab: int):
        """
        Удаление выбранного режиссёра, который человек выбирает в таблице DirectorsTableTab0
        """
        directors_list = getattr(self, f'directors_tab{tab}')
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
        directors_list = getattr(self, f'directors_tab{tab}')

        directors_table.setStyleSheet(f'background-color: {NORMAL_LINE_COLOR}')
        directors_table.clearContents()
        directors_table.setRowCount(len(directors_list))

        for row, director in enumerate(directors_list):
            for col, name in enumerate(director):
                item = QTableWidgetItem(name)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                directors_table.setItem(row, col, item)
        pprint(getattr(self, f'directors_tab{tab}'))

    def open_session_setup_dialog(self, tab: int, change=False):
        """
        Открытие окна, для добавления сеанса
        """
        table = getattr(self, f'SessionsTableTab{tab}')
        if change:
            row = table.currentRow()
            if row == -1:
                return
            date_ = getattr(self, f'selected_date_tab{tab}')
            self.session_dialog = SessionSetupDialog(self, tab, date_,
                                                     *getattr(self, f'sessions_tab{tab}')[date_][row], row)
        else:
            self.session_dialog = SessionSetupDialog(self, tab, getattr(self, f'selected_date_tab{tab}'))

        table.setCurrentCell(-1, -1)
        self.session_dialog.show()

    def set_session(self, tab: int, date_: date, time_: time, hall: int, index: int):
        """
        Добавление сенса в определенный день
        """
        sessions = getattr(self, f'sessions_tab{tab}')
        if index == -1:
            if date_ not in sessions:
                sessions[date_] = []
            sessions[date_].append((time_, hall))
        else:
            sessions[date_][index] = (time_, hall)

        sessions[date_].sort(key=lambda x: x[0].minute)
        sessions[date_].sort(key=lambda x: x[0].hour)

        pprint(getattr(self, f'sessions_tab{tab}'))
        self.load_sessions_table(tab)

    def delete_session(self, tab: int):
        """
        Удаление выбранного сеанса, выбранного в таблице
        """
        table = getattr(self, f'SessionsTableTab{tab}')
        sessions = getattr(self, f'sessions_tab{tab}')
        selected_date = getattr(self, f'selected_date_tab{tab}')

        ind = table.currentRow()
        if ind == -1:
            return

        del sessions[selected_date][ind]
        table.setCurrentCell(-1, -1)

        self.load_sessions_table(tab)

    def load_sessions_table(self, tab=0):
        """
        Загрузка сеансов, если они есть в определнггый день
        """
        attrs = ('SessionsTableTab{}', 'selected_date_tab{}', 'sessions_tab{}', 'SessionsErrorLabelTab{}')
        sessions_table, selected_date, sessions, sessions_error_label = \
            map(lambda i: getattr(self, i.format(tab)), attrs)

        # Загрузка сеансов
        sessions_table.clearContents()
        sessions_table.setRowCount(0)

        if selected_date in sessions:
            sessions_table.setRowCount(len(sessions[selected_date]))

            for row_ind in range(len(sessions[selected_date])):
                time_, hall = sessions[selected_date][row_ind]
                session_info = [QTableWidgetItem(time_.strftime('%H:%M')), QTableWidgetItem(str(hall))]

                for col_ind in range(len(session_info)):
                    session_info[col_ind].setFlags(session_info[col_ind].flags() ^ Qt.ItemIsEditable)
                    sessions_table.setItem(row_ind, col_ind, session_info[col_ind])

        sessions_error_label.setText('')
        sessions_error_label.setStyleSheet(f'background-color: {NORMAL_WINDOW_COLOR}')

    def set_selected_date(self, tab: int):
        calendar = getattr(self, f'CalendarTab{tab}')
        selected_date = calendar.selectedDate()

        if tab == 0:
            self.selected_date_tab0 = date(selected_date.year(), selected_date.month(), selected_date.day())
        else:
            self.selected_date_tab1 = date(selected_date.year(), selected_date.month(), selected_date.day())

    def load_image(self):
        """
        Получение изображения
        """
        self.ImageErrorLabelTab0.clear()
        path_to_image = QFileDialog.getOpenFileName(  # Используется при сохранении фильма
            self, 'Выбрать картинку', '',
            'Изображение (*.jpg);;Изображение (*.jpeg);;Изображение (*.png)')[0]
        if not path_to_image:
            return

        self.image_path_tab0 = path_to_image
        image = QPixmap(self.image_path_tab0)

        image_label_width, image_label_height = (self.ImageLabelTab0.geometry().width(),
                                                 self.ImageLabelTab0.geometry().height())
        w, h = image.width(), image.height()
        # Проверка, подходит ли изображение
        # Соотношение стороно должно быть 7:10 (или близко к этому)
        # И картика должна быть больше или равна по размерам ImageLabelTab0
        if RIGHT_IMAGE_WIDTH / RIGHT_IMAGE_HEIGHT + 0.15 > w / h > RIGHT_IMAGE_WIDTH / RIGHT_IMAGE_HEIGHT - 0.15 \
                and h >= 400 and w >= 280:
            resized_image = image.scaled(image_label_width, image_label_height)
            self.ImageLabelTab0.setPixmap(resized_image)
        else:
            self.ImageErrorLabelTab0.setText('Изображение не подходит.\n'
                                             'Соотношение сторон должно быть\n'
                                             '7:10.')

    def delete_image(self):
        """
        Отмена выбранного изображения
        """
        self.image_path_tab0 = ''
        self.ImageLabelTab0.clear()

    def confirm_info_press(self):
        """
        Подтвеждение введенной информации
        """
        if self.info_verification():
            title = ' '.join(self.NameLineTab0.text().strip().split())
            country = ' '.join(self.CountryLineTab0.text().strip().split())
            system_film_name = self.transcription_name_into_english(title)

            file_folder_names = list(map(lambda x: x[0], self.projectDB_cur.execute(
                """SELECT file_folder_name FROM Films""").fetchall()))
            if system_film_name in file_folder_names:  # Проверка, есть ли фильм уже в базе
                self.ErrorLabelTab0.setText('Такой фильм уже есть в базе')
                self.ErrorLabelTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')
                return

            description = self.DescriptionPlainTextTab0.toPlainText()
            age_rating, duration = map(lambda spin_box: spin_box.value(), self.SpinBoxesTab0)

            # Запись информации о фильме в таблицы
            film_id = self.filling_data(title, country, age_rating, duration, system_film_name, description)
            self.filling_genres(film_id)
            self.filling_directors(film_id)
            self.filling_sessions(film_id)
            self.clear_info()
            self.clear_fields()
        else:
            self.specifying_invalid_fields()

    def info_verification(self):
        """
        Проверка данных
        """
        lines_not_empty = all(line.text().strip() for line in self.LinesTab0)
        plains_not_empty = all(plain_text.toPlainText().strip() for plain_text in self.PlainTextsTab0)

        title_isalnum = ''.join(self.NameLineTab0.text().split()).isalnum()
        country_isalpha = ''.join(self.CountryLineTab0.text().split()).isalpha()

        image_path_not_empty = self.image_path_tab0 and self.sessions_tab0 and self.directors_tab0
        return all([lines_not_empty, title_isalnum, country_isalpha,
                    plains_not_empty, image_path_not_empty])

    def specifying_invalid_fields(self):
        """
        Указание пустых полей или неправильно заполненных полей
        """
        for line in self.LinesTab0:
            line.setStyleSheet(
                f'background-color: {ERROR_COLOR if not line.text().strip() else NORMAL_LINE_COLOR}')

        for plain_text in self.PlainTextsTab0:
            plain_text.setStyleSheet(
                f'background-color: {ERROR_COLOR if not plain_text.toPlainText().strip() else NORMAL_LINE_COLOR}')

        if not ''.join(self.NameLineTab0.text().split()).isalnum():
            self.NameLineTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not ''.join(self.CountryLineTab0.text().split()).isalpha():
            self.CountryLineTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not self.directors_tab0:
            self.DirectorsTableTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not self.image_path_tab0:
            self.ImageErrorLabelTab0.setText('Выберите постера фильма в\nпримерном соотношении сторон 7:10')

        if not self.sessions_tab0:
            self.SessionsErrorLabelTab0.setText('Добавте хотя-бы 1 сеанс')
            self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

    def filling_data(self, name: str, country: str, age_rating: int,
                     duration: int, system_film_name: str, description: str):
        """
        Запись основной информации в базу данных
        """
        os.mkdir(f'Films\\{system_film_name}')
        description_file_name = f'{system_film_name}Description.txt'
        image_name = f'{system_film_name}.png'

        with open(f'Films\\{system_film_name}\\{description_file_name}', 'w') as description_file:
            description_file.write(description)

        im = Image.open(self.image_path_tab0)
        im2 = im.resize((self.ImageLabelTab0.geometry().width(), self.ImageLabelTab0.geometry().height()))
        im2.save(f'Films\\{system_film_name}\\{image_name}')

        self.projectDB_cur.execute("INSERT INTO Films(title, country, rating, duration, file_folder_name,"
                                   " description_file_name, image_name) VALUES(?, ?, ?, ?, ?, ?, ?)",
                                   (name, country, age_rating, duration, system_film_name,
                                    description_file_name, image_name))
        self.projectDB.commit()

        film_id = self.projectDB_cur.execute("""SELECT film_id FROM Films WHERE file_folder_name = ?""",
                                             (system_film_name,)).fetchone()[0]
        return film_id

    def filling_genres(self, film_id: int):
        """
        Запись жанров фильма в таблицу Films_Genres.
        """
        write_genres = f"INSERT INTO Films_Genres VALUES({film_id}, ?)"
        for genre_id in self.genres_tab0:
            self.projectDB_cur.execute(write_genres, (genre_id,))
            self.projectDB.commit()

    def filling_directors(self, film_id: int):
        """
        Запись режиссеров фильма в таблицу Films_Directors
        """
        write_directors = f"INSERT INTO Films_Directors(film_id, name, surname) VALUES({film_id}, ?, ?)"
        for name, surname in self.directors_tab0:
            self.projectDB_cur.execute(write_directors, (name, surname))
            self.projectDB.commit()

    def filling_sessions(self, film_id: int):
        """
        Запись сеансов в таблицу Sessions
        """
        dates = sorted(self.sessions_tab0.keys())
        for date_ in dates:
            year, month, day = date_.year, date_.month, date_.day
            sessions = sorted(self.sessions_tab0[date_])
            for time_, hall in sessions:
                hour, minute = time_.hour, time_.minute

                self.projectDB_cur.execute("""INSERT INTO Sessions(year, month, day, hour, minute, film_id, hall_id) 
                                VALUES(?, ?, ?, ?, ?, ?, ?)""", (year, month, day, hour, minute, film_id, hall))
                self.projectDB.commit()

    def clear_info(self):
        """
        Очистка всей информации о фильме, записанная внутри класса
        """
        self.image_path_tab0 = ''
        self.sessions_tab0 = dict()
        self.genres_tab0.clear()
        self.directors_tab0.clear()

    def clear_fields(self):
        """
        Очещение всех полей
        """
        for line in self.LinesTab0:
            line.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
            line.setText('')
        for plaintext in self.PlainTextsTab0:
            plaintext.setPlainText('')
            plaintext.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

        self.AgeRatingSpinBoxTab0.setValue(0)
        self.DurationSpinBoxTab0.setValue(30)

        # self.load_directors_table()
        self.load_sessions_table()

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

        self.ImageErrorLabelTab0.setText('')
        self.ImageLabelTab0.clear()

    @staticmethod
    def transcription_name_into_english(name: str):
        """
        Перевод русских слов на английскую транскрипцию для удобного хранения
        """
        name = name.strip()
        dictionary = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z',
                      'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
                      'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
                      'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'u', 'я': 'ja', 'a': 'a', 'b': 'b', 'c': 'c',
                      'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l',
                      'm': 'm', 'n': 'n', 'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u',
                      'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z', '0': '0', '1': '1', '2': '2', '3': '3',
                      '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'}
        eng_name = ''
        for i in name:
            if i.lower() in dictionary:
                eng_name += dictionary[i.lower()].capitalize() if i.isupper() else dictionary[i]
            else:
                eng_name += ' '
        eng_name = eng_name.strip()
        eng_name = ''.join(map(lambda x: x.capitalize(), eng_name.split()))
        return eng_name

    def closeEvent(self, event):
        self.projectDB.close()
