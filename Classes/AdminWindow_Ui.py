import sqlite3 as sql
from datetime import datetime, date, timedelta, time
import os
import os.path
from PIL import Image

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QTabWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from Classes.Consts import *
from Classes.DirectorsSetupWindow_Ui import DirectorSetupWindow
from Classes.GenreSelectionWindow_Ui import GenresSelectionWindow
from Classes.SessionSetupWindow_Ui import SessionSetupWindow


class AdminWindow(QTabWidget):
    """
    Основное окно админа, где можно добавлять, изменять и удалять фильмы
    """
    def __init__(self):
        super().__init__()
        self.ERROR_COLOR = '#ff5133'
        self.NORMAL_COLOR = '#ffffff'
        self.MAX_DIRECTORS = 10
        self.MAX_SESSIONS = 6

        self.GenresSelectionWindowTab0 = GenresSelectionWindow()
        self.GenresSelectionWindowTab1 = GenresSelectionWindow()

        self.path_to_image_tab0 = ''
        self.genres_tab0 = []
        self.directors_tab0 = []
        self.sessions_tab0 = {}

        self.path_to_image_tab1 = ''
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
        self.selected_date_tab0 = (date_tab0.year(), date_tab0.month(), date_tab0.day())

        self.LinesTab1 = (self.CountryLineTab1, self.NameLineTab1, self.GenresLineTab1)
        self.PlainTextsTab1 = (self.DescriptionPlainTextTab1,)
        self.SpinBoxesTab1 = (self.AgeRatingSpinBoxTab1, self.DurationSpinBoxTab1)
        self.selected_date_tab1 = (date_tab1.year(), date_tab1.month(), date_tab1.day())

        self.setFixedSize(self.size())
        self.init_tab0_ui()
        self.init_tab1_ui()
        self.init_tab2_ui()

    def init_tab0_ui(self) -> None:
        """
        Инициализация для вкладки Tab0
        """
        self.GenresSelectionWindowTab0.communicate.signal.connect(self.add_genres)
        self.GenresBtnTab0.clicked.connect(self.open_genres_window)

        self.DirectorsTableTab0.setHorizontalHeaderLabels(["Имя", "Фамилия"])
        for i in range(self.DirectorsTableTab0.columnCount()):
            self.DirectorsTableTab0.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.AddDirectorBtnTab0.clicked.connect(self.open_add_director_window)
        self.ChangeDirectorsBtnTab0.clicked.connect(self.open_change_director_window)
        self.DeleteDirectorBtnTab0.clicked.connect(self.delete_director)

        for field in self.LinesTab0 + self.PlainTextsTab0:
            field.textChanged.connect(self.set_line_text_back_color)

        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.CalendarTab0.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.CalendarTab0.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        self.CalendarTab0.selectionChanged.connect(self.load_sessions_table)

        self.AddSessionBtnTab0.clicked.connect(self.open_add_session_setup_window)
        self.ChangeSessionBtnTab0.clicked.connect(self.open_change_session_setup_window)
        self.DeleteSessionBtnTab0.clicked.connect(self.delete_session)

        self.SessionsTableTab0.setHorizontalHeaderLabels(["Время", "Зал"])
        for i in range(self.SessionsTableTab0.columnCount()):
            self.SessionsTableTab0.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.LoadImageBtnTab0.clicked.connect(self.load_image)
        self.DeleteImageBtnTab0.clicked.connect(self.delete_image)

        self.ConfirmFilmInfoBtnTab0.clicked.connect(self.confirm_info_press)

    def init_tab1_ui(self) -> None:
        """
        Инициализация для вкладки Tab1
        """
        #  self.GenresSelectionWindowTab1.signal.connect()
        #  self.GenresBtnTab1.clicked.connect()

        self.DirectorsTableTab1.setHorizontalHeaderLabels(["Имя", "Фамилия"])
        for i in range(self.DirectorsTableTab1.columnCount()):
            self.DirectorsTableTab1.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        #  self.AddDirectorBtnTab1.clicked.connect()
        #  self.ChangeDirectorsBtnTab1.clicked.connect()
        #  self.DeleteDirectorBtnTab1.clicked.connect()

        for field in self.LinesTab1 + self.PlainTextsTab1:
            field.textChanged.connect(self.set_line_text_back_color)

        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.CalendarTab1.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.CalendarTab1.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        self.CalendarTab1.selectionChanged.connect(self.load_sessions_table)

        self.SessionsTableTab1.setHorizontalHeaderLabels(["Время", "Зал"])
        for i in range(self.SessionsTableTab1.columnCount()):
            self.SessionsTableTab1.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        #  self.LoadImageBtnTab1.clicked.connect()
        #  self.DeleteImageBtnTab1.clicked.connect()

        #  self.ConfirmFilmInfoBtnTab1.clicked.connect()

    def init_tab2_ui(self) -> None:
        """
        Инициализация для вкладки Tab2
        """
        pass

    def set_line_text_back_color(self) -> None:
        """
        Изменение цвета поля при введении текста
        """
        if self.sender().styleSheet() != self.NORMAL_COLOR:
            self.sender().setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
        if self.ErrorLabelTab0.styleSheet() != self.NORMAL_COLOR:
            self.ErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
        self.ErrorLabelTab0.setText('')

    def open_genres_window(self) -> None:
        """
        Открытие окна для выбора жанров
        """
        self.GenresSelectionWindowTab0.show()

    def add_genres(self) -> None:
        """
        Получение списка с жанрами
        """
        selected_genres = self.GenresSelectionWindowTab0.get_selected_genres()
        self.genres_tab0 = selected_genres.copy()
        str_genres = []
        for genre_id in self.genres_tab0:
            try:
                str_genres.append(str(self.projectDB_cur.execute("""SELECT title FROM Genres WHERE genre_id = ?""",
                                                                 (genre_id,)).fetchone()[0]))
            except TypeError:
                continue

        self.GenresLineTab0.setText(', '.join(str_genres).capitalize())
        str_genres.clear()
        selected_genres.clear()

    def open_add_director_window(self) -> None:
        """
        Открыввется окно для добавления режиссера
        """
        try:
            self.ChangeDirectorSetupWindowTab0.close()
        except AttributeError:
            pass

        self.AddDirectorSetupWindowTab0 = DirectorSetupWindow('Добавить режиссёра')
        self.AddDirectorSetupWindowTab0.communicate.signal.connect(self.add_director)
        self.AddDirectorSetupWindowTab0.show()

        self.DirectorsTableTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
        if len(self.directors_tab0) in range(self.MAX_DIRECTORS + 1):
            self.AddDirectorSetupWindowTab0.show()
        else:
            self.AddDirectorSetupWindowTab0.close()

    def add_director(self) -> None:
        """
        Добавление режиссера в список, максимум self.MAX_DIRECTORS
        """
        director_info = self.AddDirectorSetupWindowTab0.get_director()
        if director_info not in self.directors_tab0 and len(self.directors_tab0) in range(self.MAX_DIRECTORS):
            self.directors_tab0.append(director_info)
            self.directors_tab0.sort()

        self.AddDirectorSetupWindowTab0.close()
        self.load_directors_table()

    def open_change_director_window(self) -> None:
        """
        Открывается окно для изменения режиссера, который человек выбирает в таблице DirectorsTableTab0
        """
        try:
            self.AddDirectorSetupWindowTab0.close()
        except AttributeError:
            pass

        row_index = self.DirectorsTableTab0.currentRow()
        if not self.directors_tab0 or row_index < 0:
            return
        name, surname = list(map(lambda col_index: self.DirectorsTableTab0.item(row_index, col_index).text(),
                                 range(self.DirectorsTableTab0.columnCount())))

        self.ChangeDirectorSetupWindowTab0 = DirectorSetupWindow('Изменить режиссёра', row_index,
                                                                 name=name, surname=surname)
        self.ChangeDirectorSetupWindowTab0.communicate.signal.connect(self.change_director)
        self.ChangeDirectorSetupWindowTab0.show()

    def change_director(self) -> None:
        """
        Изменение выбранного режиссёра по индексу выбранной строки
        """
        director_info = self.ChangeDirectorSetupWindowTab0.get_director()

        if director_info not in self.directors_tab0:
            index, name, surname = director_info
            self.directors_tab0[index] = (name, surname)

        self.ChangeDirectorSetupWindowTab0.close()
        self.load_directors_table()

    def delete_director(self) -> None:
        """
        Удаление выбранного режиссёра, который человек выбирает в таблице DirectorsTableTab0
        """

        try:
            self.AddDirectorSetupWindowTab0.close()
        except AttributeError:
            pass

        try:
            self.ChangeDirectorSetupWindowTab0.close()
        except AttributeError:
            pass

        row_index = self.DirectorsTableTab0.currentRow()
        if not self.directors_tab0 or row_index < 0:
            return

        del self.directors_tab0[row_index]
        self.load_directors_table()

    def load_directors_table(self) -> None:
        """
        Загрузка таблицы с режиссёрами
        """
        self.DirectorsTableTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
        self.DirectorsTableTab0.clearContents()
        self.DirectorsTableTab0.setRowCount(len(self.directors_tab0))

        for row_ind, director in enumerate(self.directors_tab0):
            for col_ind, name in enumerate(director):
                item = QTableWidgetItem(name)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.DirectorsTableTab0.setItem(row_ind, col_ind, item)

    def open_add_session_setup_window(self) -> None:
        """
        Открытие окна, для добавления сеанса
        """
        try:
            self.ChangeSessionSetupWindow.close()
        except AttributeError:
            pass

        try:
            if len(self.sessions_tab0[self.selected_date_tab0]) == self.MAX_SESSIONS:
                return
        except KeyError:
            pass

        try:
            if self.sessions_tab0[self.selected_date_tab0]:
                self.AddSessionSetupWindow = SessionSetupWindow('Добавить сеанс', self.selected_date_tab0, -1,
                                                                *self.sessions_tab0[self.selected_date_tab0][-1])
            else:
                self.AddSessionSetupWindow = SessionSetupWindow('Добавить сеанс', self.selected_date_tab0)
        except KeyError:
            self.AddSessionSetupWindow = SessionSetupWindow('Добавить сеанс', self.selected_date_tab0)

        self.AddSessionSetupWindow.session_signal.connect(self.add_session)
        self.AddSessionSetupWindow.show()

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

    def add_session(self) -> None:
        """
        Добавление сенса в определенный день (в день максимум self.MAX_SESSIONS сеансов)
        """
        date_, session = self.AddSessionSetupWindow.get_session()
        if date_ in self.sessions_tab0:
            if len(self.sessions_tab0[date_]) in range(6) and session not in self.sessions_tab0[date_]:
                self.sessions_tab0[date_].append(session)
                self.sessions_tab0[date_].sort()
        else:
            self.sessions_tab0[date_] = [session]
        self.AddSessionSetupWindow.close()
        self.load_sessions_table()

    def open_change_session_setup_window(self) -> None:
        """
        Открывается окно для изменения сеанса, которые был выбран в таблице
        """
        try:
            self.AddSessionSetupWindow.close()
        except AttributeError:
            pass

        index = self.SessionsTableTab0.currentRow()
        if index < 0:
            return

        session = self.sessions_tab0[self.selected_date_tab0][index]
        self.ChangeSessionSetupWindow = SessionSetupWindow('Изменить сеанс', self.selected_date_tab0, index, *session)
        self.ChangeSessionSetupWindow.session_signal.connect(self.change_session)
        self.ChangeSessionSetupWindow.show()

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

    def change_session(self) -> None:
        """
        Изменение сеанса в определенный день
        """
        index, date_, session = self.ChangeSessionSetupWindow.get_session()
        if date_ in self.sessions_tab0:
            if session not in self.sessions_tab0[date_]:
                self.sessions_tab0[date_][index] = session
                self.sessions_tab0[date_].sort()
        else:
            self.sessions_tab0[date_] = [session]
        self.ChangeSessionSetupWindow.close()
        self.load_sessions_table()

    def delete_session(self) -> None:
        """
        Удаление выбранного сеанса, выбранного в таблице
        """
        index = self.SessionsTableTab0.currentRow()
        if index < 0:
            return

        try:
            self.ChangeSessionSetupWindow.close()
        except AttributeError:
            pass

        try:
            self.AddSessionSetupWindow.close()
        except AttributeError:
            pass

        del self.sessions_tab0[self.selected_date_tab0][index]
        if not self.sessions_tab0[self.selected_date_tab0]:
            del self.sessions_tab0[self.selected_date_tab0]

        self.load_sessions_table()

    def load_sessions_table(self) -> None:
        """
        Загрузка сеансов, если они есть в определнггый день
        """
        selected_date = self.CalendarTab0.selectedDate()
        self.selected_date_tab0 = (selected_date.year(), selected_date.month(), selected_date.day())

        # Загрузка сеансов
        self.SessionsTableTab0.clearContents()
        self.SessionsTableTab0.setRowCount(0)
        if self.selected_date_tab0 in self.sessions_tab0:
            self.SessionsTableTab0.setRowCount(len(self.sessions_tab0[self.selected_date_tab0]))
            for row_ind in range(len(self.sessions_tab0[self.selected_date_tab0])):
                hour, minute, hall = self.sessions_tab0[self.selected_date_tab0][row_ind]
                session_info = [QTableWidgetItem(time(hour, minute, 0).strftime('%H:%M')), QTableWidgetItem(str(hall))]

                for col_ind in range(len(session_info)):
                    session_info[col_ind].setFlags(session_info[col_ind].flags() ^ Qt.ItemIsEditable)
                    self.SessionsTableTab0.setItem(row_ind, col_ind, session_info[col_ind])

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

    def load_image(self) -> None:
        """
        Получение изображения
        """
        self.ImageErrorLabelTab0.clear()
        path_to_image = QFileDialog.getOpenFileName(  # Используется при сохранении фильма
            self, 'Выбрать картинку', '',
            'Изображение (*.jpg);;Изображение (*.jpeg);;Изображение (*.png)')[0]
        if not path_to_image:
            return

        self.path_to_image_tab0 = path_to_image
        image = QPixmap(self.path_to_image_tab0)

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
            self.ImageErrorLabelTab0.setText('Изображение не подходит.\nСоотношение сторон должно быть\n7:10.')

    def delete_image(self) -> None:
        """
        Отмена выбранного изображения
        """
        self.path_to_image_tab0 = ''
        self.ImageLabelTab0.clear()

    def confirm_info_press(self) -> None:
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

    def info_verification(self) -> bool:
        """
        Проверка данных
        """
        lines_not_empty = all(line.text().strip() for line in self.LinesTab0)
        plains_not_empty = all(plain_text.toPlainText().strip() for plain_text in self.PlainTextsTab0)

        title_isalnum = ''.join(self.NameLineTab0.text().split()).isalnum()
        country_isalpha = ''.join(self.CountryLineTab0.text().split()).isalpha()

        path_sessions_directors_not_empty = self.path_to_image_tab0 and self.sessions_tab0 and self.directors_tab0
        return all([lines_not_empty, title_isalnum, country_isalpha,
                    plains_not_empty, path_sessions_directors_not_empty])

    def specifying_invalid_fields(self) -> None:
        """
        Указание пустых полей или неправильно заполненных полей
        """
        for line in self.LinesTab0:
            line.setStyleSheet(
                f'background-color: {ERROR_COLOR if not line.text().strip() else self.NORMAL_COLOR}')

        for plain_text in self.PlainTextsTab0:
            plain_text.setStyleSheet(
                f'background-color: {ERROR_COLOR if not plain_text.toPlainText().strip() else self.NORMAL_COLOR}')

        if not ''.join(self.NameLineTab0.text().split()).isalnum():
            self.NameLineTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not ''.join(self.CountryLineTab0.text().split()).isalpha():
            self.CountryLineTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not self.directors_tab0:
            self.DirectorsTableTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

        if not self.path_to_image_tab0:
            self.ImageErrorLabelTab0.setText('Выберите постера фильма в\nпримерном соотношении сторон 7:10')

        if not self.sessions_tab0:
            self.SessionsErrorLabelTab0.setText('Добавте хотя-бы 1 сеанс')
            self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {ERROR_COLOR}')

    def filling_data(self, name: str, country: str, age_rating: int,
                     duration: int, system_film_name: str, description: str) -> int:
        """
        Запись основной информации в базу данных
        """
        os.mkdir(f'Films\\{system_film_name}')
        description_file_name = f'{system_film_name}Description.txt'
        image_name = f'{system_film_name}.png'

        with open(f'Films\\{system_film_name}\\{description_file_name}', 'w') as description_file:
            description_file.write(description)

        im = Image.open(self.path_to_image_tab0)
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

    def filling_genres(self, film_id: int) -> None:
        """
        Запись жанров фильма в таблицу Films_Genres.
        """
        write_genres = f"INSERT INTO Films_Genres VALUES({film_id}, ?)"
        for genre_id in self.genres_tab0:
            self.projectDB_cur.execute(write_genres, (genre_id,))
            self.projectDB.commit()

    def filling_directors(self, film_id: int) -> None:
        """
        Запись режиссеров фильма в таблицу Films_Directors
        """
        write_directors = f"INSERT INTO Films_Directors(film_id, name, surname) VALUES({film_id}, ?, ?)"
        for name, surname in self.directors_tab0:
            self.projectDB_cur.execute(write_directors, (name, surname))
            self.projectDB.commit()

    def filling_sessions(self, film_id: int) -> None:
        """
        Запись сеансов в таблицу Sessions
        """
        dates = sorted(self.sessions_tab0.keys())
        for date1 in dates:
            year, month, day = date1
            sessions = sorted(self.sessions_tab0[date1])
            for hour, minute, hall in sessions:
                self.projectDB_cur.execute("""INSERT INTO Sessions(year, month, day, hour, minute, film_id, hall_id) 
                                VALUES(?, ?, ?, ?, ?, ?, ?)""", (year, month, day, hour, minute, film_id, hall))
                self.projectDB.commit()

    def clear_info(self) -> None:
        """
        Очистка всей информации о фильме, записанная внутри класса
        """
        self.path_to_image_tab0 = ''
        self.sessions_tab0 = dict()
        self.genres_tab0.clear()
        self.directors_tab0.clear()

    def clear_fields(self) -> None:
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

        self.load_directors_table()
        self.load_sessions_table()

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

        self.ImageErrorLabelTab0.setText('')
        self.ImageLabelTab0.clear()

    @staticmethod
    def transcription_name_into_english(name: str) -> str:
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

    def closeEvent(self, event) -> None:
        self.GenresSelectionWindowTab0.close()
        if hasattr(self, 'AddDirectorSetupWindowTab0'):
            self.AddDirectorSetupWindowTab0.close()

        if hasattr(self, 'ChangeDirectorSetupWindowTab0'):
            self.ChangeDirectorSetupWindowTab0.close()

        if hasattr(self, 'AddSessionSetupWindow'):
            self.AddSessionSetupWindow.close()

        if hasattr(self, 'ChangeSessionSetupWindow'):
            self.ChangeSessionSetupWindow.close()

        self.projectDB.close()
        self.close()
