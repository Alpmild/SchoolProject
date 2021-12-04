import sys
import sqlite3 as sql
from datetime import datetime, date, timedelta, time
import os
import os.path
from PIL import Image

from PyQt5.QtCore import Qt, pyqtSignal, QDate, QTime, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QStatusBar, QLineEdit, QTabWidget, QFileDialog
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QPixmap
from PyQt5 import uic


NORMAL_LINE_COLOR = '#ffffff'
NORMAL_WINDOW_COLOR = '#f0f0f0'
ERROR_COLOR = '#ff5133'


class StartWindow(QMainWindow):
    """
    Стартовое окно
    """
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('Interfaces\\StartWindow.ui', self)
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Стартовое окно приложения')
        self.UserLoginBtn.clicked.connect(self.open_user_window)
        self.AdminLoginBtn.clicked.connect(self.open_login_window)

    def open_user_window(self) -> None:
        """
        Человек сразу заходит в приложение и начинает им пользоваться
        """
        self.UserWin = UserWindow()
        self.UserWin.show()
        self.close()

    def open_login_window(self) -> None:
        """
        Открывается окно подтверждения -> LoginWindow
        """
        self.LgnWin = LoginWindow()
        self.LgnWin.show()
        self.close()


class LoginWindow(QMainWindow):
    """
    Окно входа в аккаунт папы-админа :)
    """
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.statusBar = QStatusBar()
        uic.loadUi('Interfaces\\LoginWindow.ui', self)
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Вход в систему')
        self.ComeInBtn.clicked.connect(self.come_in_press)
        self.CancelBtn.clicked.connect(self.cancel_press)
        self.PasswordLine.setEchoMode(QLineEdit.Password)

    def come_in_press(self) -> None:
        """
        Проверка данных для входа в систему
        """
        login, password = self.LoginLine.text(), self.PasswordLine.text()
        if not login or not password:
            return
        db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        info = {x[0]: x[1] for x in db.execute("""SELECT login, password FROM admins_data""").fetchall()}
        try:
            assert login in info and info[login] == password
            self.AdminWindow = AdminWindow()
            self.AdminWindow.show()
            self.close()
        except AssertionError:
            self.statusBar.showMessage('Неверное имя аккаунта или пароль.')
            self.PasswordLine.setText('')
        db.close()

    def cancel_press(self) -> None:
        self.close()


class AdminWindow(QTabWidget):
    """
    Основное окно админа, где можно добавлять, изменять и удалять фильмы
    """
    def __init__(self):
        super().__init__()
        self.GenresSelectionWindow = GenresSelectionWindow()

        self.ERROR_COLOR = '#ff5133'
        self.NORMAL_COLOR = '#ffffff'
        self.MAX_DIRECTORS = 10
        self.MAX_SESSIONS = 6
        self.RIGHT_WIDTH, self.RIGHT_HEIGHT = (280, 400)

        self.path_to_image = ''
        self.genres = []
        self.directors = []
        self.sessions = dict()

        self.projectDB = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.projectDB_cur = self.projectDB.cursor()

        uic.loadUi('Interfaces\\MainAdminWindowRework.ui', self)
        self.LinesTab0 = (self.CountryLineTab0, self.NameLineTab0, self.GenresLineTab0)
        self.PlainTextsTab0 = (self.DescriptionPlainTextTab0,)
        self.SpinBoxesTab0 = (self.AgeRatingSpinBoxTab0, self.DurationSpinBoxTab0)

        self.init_tab0_ui()
        self.init_tab1_ui()
        self.init_tab2_ui()

    def init_tab0_ui(self) -> None:
        """
        Инициализация для страницы Tab0
        """
        self.setWindowTitle('Редактировние данных')
        self.setFixedSize(self.size())

        self.GenresSelectionWindow.signal.connect(self.add_genres)
        self.GenresBtnTab0.clicked.connect(self.open_genres_window)

        self.DirectorsTableWidgetTab0.setHorizontalHeaderLabels(["Имя", "Фамилия"])
        for i in range(self.DirectorsTableWidgetTab0.columnCount()):
            self.DirectorsTableWidgetTab0.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.AddDirectorBtnTab0.clicked.connect(self.open_add_director_window)
        self.ChangeDirectorsBtnTab0.clicked.connect(self.open_change_director_window)
        self.DeleteDirectorBtnTab0.clicked.connect(self.delete_director)

        for line in self.LinesTab0 + self.PlainTextsTab0:
            line.textChanged.connect(self.set_line_text_back_color)

        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.CalendarTab0.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.CalendarTab0.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        self.CalendarTab0.selectionChanged.connect(self.load_sessions_table)

        self.AddSessionBtnTab0.clicked.connect(self.open_add_session_setup_window)
        self.ChangeSessionBtnTab0.clicked.connect(self.open_change_session_setup_window)
        self.DeleteSessionBtnTab0.clicked.connect(self.delete_session)

        self.SessionsTableWidgetTab0.setHorizontalHeaderLabels(["Время", "Зал"])
        for i in range(self.SessionsTableWidgetTab0.columnCount()):
            self.SessionsTableWidgetTab0.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.LoadImageBtnTab0.clicked.connect(self.load_image)
        self.DeleteImageBtnTab0.clicked.connect(self.delete_image)

        self.ConfirmFilmInfoBtnTab0.clicked.connect(self.confirm_info_press)

    def init_tab1_ui(self) -> None:
        """
        Инициализация для страницы Tab1
        """
        pass

    def init_tab2_ui(self) -> None:
        """
        Инициализация для страницы Tab2
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
        self.GenresSelectionWindow.show()

    def add_genres(self) -> None:
        """
        Получение списка с жанрами
        """
        selected_genres = self.GenresSelectionWindow.confirm_genres_press()
        if selected_genres:
            self.GenresLineTab0.setText(', '.join(selected_genres).capitalize())
            self.genres = selected_genres.copy()

            self.GenresSelectionWindow.statusBar.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
            self.GenresSelectionWindow.statusBar.showMessage('')
            self.GenresSelectionWindow.close()
        else:
            self.GenresSelectionWindow.statusBar.showMessage('Выберите хотя-бы 1 жанр')
            self.GenresSelectionWindow.statusBar.setStyleSheet(f'background-color: {self.ERROR_COLOR}')

    def open_add_director_window(self) -> None:
        """
        Открыввется окно для добавления режиссера
        """
        if hasattr(self, 'ChangeDirectorSetupWindow'):
            self.ChangeDirectorSetupWindow.close()

        self.AddDirectorSetupWindow = DirectorSetupWindow('Добавить режиссёра')
        self.AddDirectorSetupWindow.communicate.signal.connect(self.add_director)
        self.AddDirectorSetupWindow.show()

        self.DirectorsTableWidgetTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
        if len(self.directors) in range(self.MAX_DIRECTORS + 1):
            self.AddDirectorSetupWindow.show()
        else:
            self.AddDirectorSetupWindow.close()

    def add_director(self) -> None:
        """
        Добавление режиссера в список, максимум self.MAX_DIRECTORS
        """
        director_info = self.AddDirectorSetupWindow.get_director()
        if director_info not in self.directors and len(self.directors) in range(self.MAX_DIRECTORS):
            self.directors.append(director_info)
            self.directors.sort()

        self.AddDirectorSetupWindow.close()
        self.load_directors_table()

    def open_change_director_window(self) -> None:
        """
        Открывается окно для изменения режиссера, который человек выбирает в таблице DirectorsTableWidgetTab0
        """
        if hasattr(self, 'AddDirectorSetupWindow'):
            self.AddDirectorSetupWindow.close()

        row_index = self.DirectorsTableWidgetTab0.currentRow()
        if not self.directors or row_index < 0:
            return
        name, surname = list(map(lambda col_index: self.DirectorsTableWidgetTab0.item(row_index, col_index).text(),
                                 range(self.DirectorsTableWidgetTab0.columnCount())))

        self.ChangeDirectorSetupWindow = DirectorSetupWindow('Изменить режиссёра', row_index,
                                                             name=name, surname=surname)
        self.ChangeDirectorSetupWindow.communicate.signal.connect(self.change_director)
        self.ChangeDirectorSetupWindow.show()

    def change_director(self) -> None:
        """
        Изменение выбранного режиссёра по индексу выбранной строки
        """
        director_info = self.ChangeDirectorSetupWindow.get_director()

        if director_info not in self.directors:
            index, name, surname = director_info
            self.directors[index] = (name, surname)

        self.ChangeDirectorSetupWindow.close()
        self.load_directors_table()

    def delete_director(self) -> None:
        """
        Удаление выбранного режиссёра, который человек выбирает в таблице DirectorsTableWidgetTab0
        """
        if hasattr(self, 'AddDirectorSetupWindow'):
            self.AddDirectorSetupWindow.close()

        if hasattr(self, 'ChangeDirectorSetupWindow'):
            self.ChangeDirectorSetupWindow.close()

        row_index = self.DirectorsTableWidgetTab0.currentRow()
        if not self.directors or row_index < 0:
            return

        del self.directors[row_index]
        self.load_directors_table()

    def load_directors_table(self) -> None:
        """
        Загрузка таблицы с режиссёрами
        """
        self.DirectorsTableWidgetTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
        self.DirectorsTableWidgetTab0.clearContents()
        self.DirectorsTableWidgetTab0.setRowCount(len(self.directors))

        for row_ind, director in enumerate(self.directors):
            for col_ind, name in enumerate(director):
                item = QTableWidgetItem(name)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.DirectorsTableWidgetTab0.setItem(row_ind, col_ind, item)

    def open_add_session_setup_window(self) -> None:
        """
        Открытие окна, для добавления сеанса
        """
        if hasattr(self, 'ChangeSessionSetupWindow'):
            if not self.ChangeSessionSetupWindow.isHidden():
                self.ChangeSessionSetupWindow.close()

        date_ = self.CalendarTab0.selectedDate()
        selected_date = (date_.year(), date_.month(), date_.day())
        try:
            if len(self.sessions[selected_date]) == self.MAX_SESSIONS:
                return
        except KeyError:
            pass

        try:
            hour, minute, hall = self.sessions[selected_date][-1]
            if self.sessions[selected_date]:
                self.AddSessionSetupWindow = SessionSetupWindow('Добавить сеанс', selected_date, hour=hour,
                                                                minute=minute, hall=hall)
            else:
                self.AddSessionSetupWindow = SessionSetupWindow('Добавить сеанс', selected_date)
        except KeyError:
            self.AddSessionSetupWindow = SessionSetupWindow('Добавить сеанс', selected_date)

        self.AddSessionSetupWindow.session_signal.connect(self.add_session)
        self.AddSessionSetupWindow.show()

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

    def add_session(self) -> None:
        """
        Добавление сенса в определенный день (в день максимум self.MAX_SESSIONS сеансов)
        """
        date_, session = self.AddSessionSetupWindow.get_session()
        if date_ in self.sessions:
            if len(self.sessions[date_]) in range(6) and session not in self.sessions[date_]:
                self.sessions[date_].append(session)
                self.sessions[date_].sort()
        else:
            self.sessions[date_] = [session]
        self.AddSessionSetupWindow.close()
        self.load_sessions_table()

    def open_change_session_setup_window(self) -> None:
        """
        Открывается окно для изменения сеанса, которые был выбран в таблице
        """
        if hasattr(self, 'AddSessionSetupWindow'):
            if not self.AddSessionSetupWindow.isHidden():
                self.AddSessionSetupWindow.close()

        index = self.SessionsTableWidgetTab0.currentRow()
        if index < 0:
            return

        date_ = self.CalendarTab0.selectedDate()
        selected_date = (date_.year(), date_.month(), date_.day())

        session = self.sessions[selected_date][index]
        self.ChangeSessionSetupWindow = SessionSetupWindow('Изменить сеанс', selected_date, index, *session)
        self.ChangeSessionSetupWindow.session_signal.connect(self.change_session)
        self.ChangeSessionSetupWindow.show()

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

    def change_session(self) -> None:
        """
        Изменение сеанса в определенный день
        """
        index, date_, session = self.ChangeSessionSetupWindow.get_session()
        if date_ in self.sessions:
            if session not in self.sessions[date_]:
                self.sessions[date_][index] = session
                self.sessions[date_].sort()
        else:
            self.sessions[date_] = [session]
        self.ChangeSessionSetupWindow.close()
        self.load_sessions_table()

    def delete_session(self) -> None:
        """
        Удаление выбранного сеанса, выбранного в таблице
        """
        index = self.SessionsTableWidgetTab0.currentRow()
        if index < 0:
            return
        date_ = self.CalendarTab0.selectedDate()

        del self.sessions[(date_.year(), date_.month(), date_.day())][index]
        self.load_sessions_table()

    def load_sessions_table(self) -> None:
        """
        Загрузка сеансов, если они есть в определнггый день
        """
        selected_date = self.CalendarTab0.selectedDate()
        year, month, day = selected_date.year(), selected_date.month(), selected_date.day()
        date_ = (year, month, day)

        # Загрузка сеансов
        self.SessionsTableWidgetTab0.clearContents()
        self.SessionsTableWidgetTab0.setRowCount(0)
        if date_ in self.sessions:
            self.SessionsTableWidgetTab0.setRowCount(len(self.sessions[date_]))
            for row_ind in range(len(self.sessions[date_])):
                hour, minute, hall = self.sessions[date_][row_ind]

                session_info = [QTableWidgetItem(time(hour, minute, 0).strftime('%H:%M')), QTableWidgetItem(str(hall))]
                for col_ind in range(len(session_info)):
                    session_info[col_ind].setFlags(session_info[col_ind].flags() ^ Qt.ItemIsEditable)
                    self.SessionsTableWidgetTab0.setItem(row_ind, col_ind, session_info[col_ind])

        self.SessionsErrorLabelTab0.setText('')
        self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')

    def load_image(self) -> None:
        """
        Получение изображения
        """
        path_to_image = QFileDialog.getOpenFileName(  # Используется при сохранении фильма
            self, 'Выбрать картинку', '',
            'Изображение (*.jpg);;Изображение (*.jpeg);;Изображение (*.png)')[0]
        if not path_to_image:
            return

        self.path_to_image = path_to_image
        image = QPixmap(self.path_to_image)

        image_label_width, image_label_height = (self.ImageLabelTab0.geometry().width(),
                                                 self.ImageLabelTab0.geometry().height())
        w, h = image.width(), image.height()
        # Проверка, подходит ли изображение
        # Соотношение стороно должно быть 7:10 (или близко к этому)
        # И картика должна быть больше или равна по размерам ImageLabelTab0
        if self.RIGHT_WIDTH / self.RIGHT_HEIGHT + 0.15 > w / h > self.RIGHT_WIDTH / self.RIGHT_HEIGHT - 0.15 \
                and h >= 400 and w >= 280:
            resized_image = image.scaled(image_label_width, image_label_height)
            self.ImageLabelTab0.setPixmap(resized_image)
        else:
            self.ImageErrorLabelTab0.setText('Изображение не подходит.\nСоотношение сторон должно быть\n7:10.')

    def delete_image(self) -> None:
        """
        Отмена выбранного изображения
        """
        self.path_to_image = ''
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
                self.ErrorLabelTab0.setStyleSheet(f'background-color: {self.ERROR_COLOR}')
                return

            description = self.DescriptionPlainTextTab0.toPlainText()
            age_rating, duration = map(lambda spin_box: spin_box.value(), self.SpinBoxesTab0)

            # Запись информации о фильме в таблицы
            film_id = self.filling_data(title, country, age_rating, duration, system_film_name, description)
            self.filling_genres(film_id)
            self.filling_directors(film_id)
            self.filling_sessions(film_id)
            self.clear_all_info()
            self.clear_all_fields()
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

        path_sessions_directors_not_empty = self.path_to_image and self.sessions and self.directors
        return all([lines_not_empty, title_isalnum, country_isalpha,
                    plains_not_empty, path_sessions_directors_not_empty])

    def specifying_invalid_fields(self) -> None:
        """
        Указание пустых полей или неправильно заполненных полей
        """
        for line in self.LinesTab0:
            line.setStyleSheet(
                f'background-color: {self.ERROR_COLOR if not line.text().strip() else self.NORMAL_COLOR}')

        for plain_text in self.PlainTextsTab0:
            plain_text.setStyleSheet(
                f'background-color: {self.ERROR_COLOR if not plain_text.toPlainText().strip() else self.NORMAL_COLOR}')

        if not ''.join(self.NameLineTab0.text().split()).isalnum():
            self.NameLineTab0.setStyleSheet(f'background-color: {self.ERROR_COLOR}')

        if not ''.join(self.CountryLineTab0.text().split()).isalpha():
            self.CountryLineTab0.setStyleSheet(f'background-color: {self.ERROR_COLOR}')

        if not self.directors:
            self.DirectorsTableWidgetTab0.setStyleSheet(f'background-color: {self.ERROR_COLOR}')

        if not self.path_to_image:
            self.ImageErrorLabelTab0.setText('Выберите постера фильма в\nпримерном соотношении сторон 7:10')

        if not self.sessions:
            self.SessionsErrorLabelTab0.setText('Добавте хотя-бы 1 сеанс')
            self.SessionsErrorLabelTab0.setStyleSheet(f'background-color: {self.ERROR_COLOR}')

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

        im = Image.open(self.path_to_image)
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
        genres = sorted(list(map(lambda x: self.projectDB_cur.execute("""SELECT genre_id FROM Genres WHERE title = ?""",
                                                                      (x,)).fetchone()[0], self.genres)))
        write_genres = f"INSERT INTO Films_Genres VALUES({film_id}, ?)"
        for genre_id in genres:
            self.projectDB_cur.execute(write_genres, (genre_id,))
            self.projectDB.commit()

    def filling_directors(self, film_id: int) -> None:
        """
        Запись режиссеров фильма в таблицу Films_Directors
        """
        write_directors = f"INSERT INTO Films_Directors(film_id, name, surname) VALUES({film_id}, ?, ?)"
        for name, surname in self.directors:
            self.projectDB_cur.execute(write_directors, (name, surname))
            self.projectDB.commit()

    def filling_sessions(self, film_id: int) -> None:
        """
        Запись сеансов в таблицу Sessions
        """
        dates = sorted(self.sessions.keys())
        for date1 in dates:
            year, month, day = date1
            sessions = sorted(self.sessions[date1])
            for hour, minute, hall in sessions:
                self.projectDB_cur.execute("""INSERT INTO Sessions(year, month, day, hour, minute, film_id, hall_id) 
                                VALUES(?, ?, ?, ?, ?, ?, ?)""", (year, month, day, hour, minute, film_id, hall))
                self.projectDB.commit()

    def clear_all_info(self) -> None:
        """
        Очистка всей информации о фильме, записанная внутри класса
        """
        self.path_to_image = ''
        self.sessions = dict()
        self.genres.clear()
        self.directors.clear()

    def clear_all_fields(self) -> None:
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
        self.ImageErrorLabelTab0.setStyleSheet(f'background-color: {self.NORMAL_COLOR}')
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
        if not self.GenresSelectionWindow.isHidden():
            self.GenresSelectionWindow.close()
        self.projectDB.close()
        self.close()


class UserWindow(QMainWindow):
    """
    Основное окно пользователя
    """
    def __init__(self):
        super().__init__()
        uic.loadUi('Interfaces\\UserWindow.ui', self)
        self.films_db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.films_cur = self.films_db.cursor()
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Выбор фильма')
        now_date = date(datetime.now().year, datetime.now().month, datetime.now().day)
        future_date = now_date + timedelta(days=30)
        self.Calendar.setMinimumDate(QDate(now_date.year, now_date.month, now_date.day))
        self.Calendar.setMaximumDate(QDate(future_date.year, future_date.month, future_date.day))
        self.Calendar.selectionChanged.connect(self.load_table_films)

        self.FilmsTableWidget.setColumnCount(4)
        self.FilmsTableWidget.setHorizontalHeaderLabels(["Называние", "Жанры", "Рейтинг", "Длительность"])
        for i in range(2):
            self.FilmsTableWidget.setColumnWidth(i, 250)
            self.FilmsTableWidget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Fixed)
        for i in range(2, 4):
            self.FilmsTableWidget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.FilmsTableWidget.itemDoubleClicked.connect(self.open_film_window)
        self.load_table_films()

    def load_table_films(self) -> None:
        """
        Загрузка таблицы в зависимости от даты
        """
        self.FilmsTableWidget.clearContents()
        films_data = self.get_films_by_date()
        self.FilmsTableWidget.setRowCount(len(films_data))

        for row_ind, row in enumerate(films_data):  # Добаввление дынных в таблицу
            title, rating, duration, genres = row
            genres = ', '.join(sorted(list(map(lambda x: self.films_cur.execute(
                """SELECT title FROM Genres WHERE genre_id = ?""", (x,)).fetchone()[0], genres)))).capitalize()

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
                self.FilmsTableWidget.setItem(row_ind, column_ind, item)

    def get_films_by_date(self) -> list:
        """
        Возвращение списка с фильмами и нужной инфой, который показывают в выбранную дату
        """
        suitable_films = []
        selected_date = (self.Calendar.selectedDate().year(), self.Calendar.selectedDate().month(),
                         self.Calendar.selectedDate().day())

        films_ids = list(map(lambda x: x[0], self.films_cur.execute("""SELECT film_id FROM Films""").fetchall()))
        sessions = self.films_cur.execute("""SELECT year, month, day, film_id FROM Sessions""").fetchall()
        for film_id in films_ids:
            if (*selected_date, film_id) in sessions:
                info = self.films_cur.execute(
                    """SELECT title, rating, duration FROM Films WHERE film_id = ?""", (film_id,)).fetchone()
                genres = tuple(i[0] for i in self.films_cur.execute(
                    """SELECT genre_id FROM Films_Genres WHERE film_id = ?""", (film_id,)).fetchall())
                suitable_films.append((*info, genres))
        return suitable_films

    def open_film_window(self, item: QTableWidgetItem) -> None:
        """
        Открытия окна фильма со всей информацией
        """
        if item.column() == 0:
            year, month, day = self.Calendar.selectedDate().year(), self.Calendar.selectedDate().month(), \
                               self.Calendar.selectedDate().day()
            film_info = self.films_cur.execute("""SELECT * FROM Films WHERE title = ?""", (item.text(),)).fetchone()

            genres = list(map(lambda x: x[0], self.films_cur.execute(
                """SELECT genre_id FROM Films_Genres WHERE film_id = ?""", (film_info[0],)).fetchall()))
            genres = tuple(map(lambda x: self.films_cur.execute("""SELECT title FROM Genres WHERE genre_id = ?""",
                                                               (x,)).fetchone()[0], genres))

            directors = tuple(self.films_cur.execute("""SELECT name, surname FROM Films_Directors WHERE film_id = ?""",
                                                     (film_info[0],)).fetchall())

            sessions = tuple(self.films_cur.execute(
                """SELECT session_id, hour, minute, hall_id FROM Sessions WHERE year = ? AND month = ? and day = ? 
                and film_id = ?""", (year, month, day, film_info[0])).fetchall())

            self.main_film_window = FilmWindow(film_info, genres, directors, sessions)
            self.main_film_window.show()

    def closeEvent(self, event):
        if hasattr(self, 'main_film_window'):
            self.main_film_window.close()
        self.films_db.close()
        self.close()


class FilmWindow(QMainWindow):
    """
    Окно фильма со всей нужной информацией для пользователя
    """
    def __init__(self, film_info: tuple, genres: tuple, directors: tuple, sessions: tuple):
        super().__init__()
        self.film_info = film_info
        self.genres = genres
        self.directors = directors
        self.sessions = sessions

        self.film_db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.film_cur = self.film_db.cursor()

        uic.loadUi('Interfaces\\FilmWindow.ui', self)
        self.info_lines = [self.NameLine, self.CountryLine, self.GenresLine,
                           self.AgeRatingLine, self.DurationLine]
        self.session_btns = [self.Session1Btn, self.Session2Btn, self.Session3Btn,
                             self.Session4Btn, self.Session5Btn, self.Session6Btn]
        self.setFixedSize(self.size())
        self.load_film_info()

    def load_film_info(self) -> None:
        """
        Загрузка информации о фильме в окно
        """
        film_id, title, country, rating, duration, file_folder_name, description_file_name, image_name \
            = self.film_info
        self.setWindowTitle(title)
        genres = ', '.join(self.genres).capitalize()
        directors = ', '.join(list(map(lambda x: ' '.join(x), self.directors)))

        hours_dur, minutes_dur = divmod(duration, 60)
        if hours_dur > 0 and minutes_dur > 0:
            duration = f'{hours_dur}ч {minutes_dur}мин.'
        elif hours_dur > 0 and minutes_dur == 0:
            duration = f'{hours_dur}ч'
        else:
            duration = f'{minutes_dur}мин.'

        description_text = ''
        try:
            with open(f'Films\\{file_folder_name}\\{description_file_name}', 'r') as description_file:
                description_text = description_file.read().replace('\n', ' ')
        except FileNotFoundError:
            pass

        # Заполнение полей с информацией о фильме
        info = [title, country, genres, f'{rating}+', duration]
        [self.info_lines[i].setText(info[i]) for i in range(len(self.info_lines))]
        info.clear()
        self.DirectorsPlainText.setPlainText(directors)
        self.DescriptionPlainText.setPlainText(description_text)
        self.ImageLabel.setPixmap(QPixmap(f'Films\\{file_folder_name}\\{image_name}'))

        # Заполнение сеансовё
        try:
            if len(self.sessions) < len(self.session_btns):
                [btn.hide() for btn in self.session_btns[len(self.sessions):]]
        except IndexError:
            pass

        try:
            for i in range(len(self.sessions)):
                ses_info = f'{time(self.sessions[i][1], self.sessions[i][2], 0).strftime("%H:%M")}\nЗал ' \
                           f'{self.sessions[i][3]}'
                self.session_btns[i].setText(ses_info)
        except IndexError:
            pass

        try:
            for i in range(len(self.sessions)):
                self.bind_btn(self.session_btns[i], self.sessions[i])
        except IndexError:
            pass

    def bind_btn(self, btn, session):
        """
        Назначение на каждую кнопку определенного сеанса
        """
        session_id = session[0]
        btn.clicked.connect(lambda: self.open_order_menu(session_id))

    def open_order_menu(self, session_id: int) -> None:  # Открывается окно зала для выбора места
        self.hallWindow = HallWindow(session_id)
        self.hallWindow.show()

    def closeEvent(self, event):
        if hasattr(self, 'hallWindow'):
            self.hallWindow.close()
        self.close()


class HallWindow(QMainWindow):
    """
    Окно зала, которое получает session_id для записи покупкт билетов
    """
    def __init__(self, session_id: int):
        super().__init__()
        self.session_id = session_id
        self.tickets_db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.tickets_cur = self.tickets_db.cursor()
        self.normal_color = '#ffffff'
        self.order_color = '#ffe666'
        self.occupied_color = '#aa0000'
        uic.loadUi('Interfaces\\HallWindow.ui', self)
        self.status_bar = QStatusBar()
        self.place_btns = [
            [self.PlaceBtn11, self.PlaceBtn12, self.PlaceBtn13, self.PlaceBtn14, self.PlaceBtn15, self.PlaceBtn16,
             self.PlaceBtn17],
            [self.PlaceBtn21, self.PlaceBtn22, self.PlaceBtn23, self.PlaceBtn24, self.PlaceBtn25, self.PlaceBtn26,
             self.PlaceBtn27],
            [self.PlaceBtn31, self.PlaceBtn32, self.PlaceBtn33, self.PlaceBtn34, self.PlaceBtn35, self.PlaceBtn36,
             self.PlaceBtn37],
            [self.PlaceBtn41, self.PlaceBtn42, self.PlaceBtn43, self.PlaceBtn44, self.PlaceBtn45, self.PlaceBtn46,
             self.PlaceBtn47],
            [self.PlaceBtn51, self.PlaceBtn52, self.PlaceBtn53, self.PlaceBtn54, self.PlaceBtn55, self.PlaceBtn56,
             self.PlaceBtn57]
        ]
        self.ordered_places = []
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setStatusBar(self.status_bar)
        self.BuyBtn.clicked.connect(self.buy_tickets)
        purchased_seats = self.tickets_cur.execute("""SELECT row, column FROM Tickets WHERE session_id = ?""",
                                                   (self.session_id,)).fetchall()
        for row_ind in range(len(self.place_btns)):
            for col_ind in range(len(self.place_btns[row_ind])):
                self.close_the_place(row_ind, col_ind,
                                     (row_ind, col_ind) in purchased_seats)

    def close_the_place(self, row_ind: int, col_ind: int, place_is_taken: bool) -> None:
        """
        Красным закрашивуются уже ранее купленный места, а остальные при нажатие добавляются в заказ
        """
        if place_is_taken:
            self.place_btns[row_ind][col_ind].setStyleSheet(f'background-color: {self.occupied_color}')
        else:
            self.place_btns[row_ind][col_ind].clicked.connect(lambda: self.order_place(row_ind, col_ind))

    def order_place(self, row_ind: int, col_ind: int) -> None:
        """
        Добавление заказываемых пользователей мест в список
        """
        if (row_ind, col_ind) in self.ordered_places:
            self.ordered_places.remove((row_ind, col_ind))
            self.place_btns[row_ind][col_ind].setStyleSheet(f'background-color: {self.normal_color}')
        else:
            self.ordered_places.append((row_ind, col_ind))
            self.place_btns[row_ind][col_ind].setStyleSheet(f'background-color: {self.order_color}')
        self.ordered_places.sort()
        self.status_bar.showMessage('')

    def buy_tickets(self) -> None:
        """
        Покупка билетов и добавление заказанных мест в базу
        """
        if self.ordered_places:
            insert_places = f"INSERT INTO Tickets VALUES({self.session_id}, ?, ?)"
            for i in self.ordered_places:
                row, col = i
                self.tickets_cur.execute(insert_places, (row, col))
                self.tickets_db.commit()

            ordered_places_copy = self.ordered_places.copy()
            self.tab_window = TabWindow(self.session_id, ordered_places_copy)
            self.tab_window.show()
            self.ordered_places.clear()
            self.close()
        else:
            self.status_bar.showMessage('Закажите хотя-бы 1 место.')


class TabWindow(QMainWindow):
    """
    Окно с кодом заказа
    """
    def __init__(self, session_id, ordered_places):
        self.session_id = session_id
        self.ordered_places = ordered_places
        super().__init__()
        uic.loadUi('Interfaces\\TabWindow.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setWindowTitle('Зал')
        unique_cod = f'{self.session_id}:{":".join(["_".join(list(map(str, i))) for i in self.ordered_places])}'
        ordered_places = '\n'.join([f'Ряд {place[0] + 1} Место {place[1] + 1}' for place in self.ordered_places])
        self.PlainTextEdit.setPlainText(f'Ваш уникальный код:\n{unique_cod}\n\nВаш заказ:\n{ordered_places}\n'
                                        f'\nСпасибо за покупку :)')


class GenresSelectionWindow(QMainWindow):
    """
    Окно выбора жанров
    """
    signal = pyqtSignal()

    def __init__(self):
        super(GenresSelectionWindow, self).__init__()
        self.selectedGenres = []
        self.statusBar = QStatusBar()
        self.db = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.cur = self.db.cursor()
        self.genres = list(map(lambda x: x[0], self.cur.execute("""SELECT title FROM genres""").fetchall()))
        uic.loadUi('Interfaces\\GenreSelectionWindow.ui', self)
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Выбор жанров')
        self.setStatusBar(self.statusBar)
        self.ConfirmSelectionBtn.clicked.connect(self.signal)  # Нажатие кнопки создает сигнал
        [self.GenresListWidget.addItem(elem) for elem in self.genres]

    def confirm_genres_press(self) -> list:
        """
        Возвращает список с выбранными жанрами
        """
        return sorted(list(map(lambda i: i.text(), self.GenresListWidget.selectedItems())))


class DirectorSetupWindow(QMainWindow):
    """
    Окно для добавления режиссёра
    """
    def __init__(self, title: str, index=-1, name='', surname=''):
        super().__init__()
        self.title = title
        self.ind = index
        self.ind_ = index
        self.first_director_info = (name, surname)

        self.error_color = '#ff5133'
        self.normal_line_color = '#ffffff'
        self.normal_window_color = '#f0f0f0'
        self.bool_error_messages = ['Заполните поле с именем', 'Заполните поле с фамилией',
                                    'Заполните поля с именем и фамилией']

        self.communicate = Communicate()
        self.statusBar = QStatusBar()
        uic.loadUi('Interfaces\\DirectorSetupWindow.ui', self)
        self.lines = (self.NameLine, self.SurnameLine)

        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle(self.title)
        self.setStatusBar(self.statusBar)

        for i, line in enumerate(self.lines):
            line.setText(self.first_director_info[i])
            line.textChanged.connect(self.set_normal_color)

        self.ConfirmDirectorBtn.clicked.connect(self.confirm_director)

    def set_normal_color(self) -> None:
        """
        Изменение цвета поля прия изменении текста в нем
        """
        self.sender().setStyleSheet(f'background-color: {self.normal_line_color}')
        self.statusBar.setStyleSheet(f'background-color: {self.normal_window_color}')
        self.statusBar.showMessage('')

    def confirm_director(self) -> None:
        """
        При нажатии на кнопку происходит проверка введенных данных.
        Если не заполнены некоторые поля, то они подсвечиваются.
        Таже ситуация с неправильно заполненными полями.
        Если все "ок", то вызывается сигнал, чтоб передать данные в родительское окно.
        """
        indexes = [i for i in range(len(self.lines)) if not ' '.join(self.lines[i].text().strip().split())]
        if indexes:
            for i in indexes:
                self.lines[i].setStyleSheet(f'background-color: {self.error_color}')
                self.lines[i].setText('')
            if len(indexes) == 1:
                self.statusBar.showMessage(self.bool_error_messages[indexes[0]])
            else:
                self.statusBar.showMessage(self.bool_error_messages[2])
            self.statusBar.setStyleSheet(f'background-color: {self.error_color}')
            return

        flag = True
        person_info = tuple(' '.join(line.text().strip().split()) for line in self.lines)
        for i in range(len(person_info)):
            if not self.indication_incorrectly_lines(person_info[i]):
                flag = False
                self.lines[i].setStyleSheet(f'background-color: {self.error_color}')

        if flag:
            self.radiate_signal()
        else:
            self.statusBar.setStyleSheet(f'background-color: {self.error_color}')
            self.statusBar.showMessage('Некорректно введены данные')

    def indication_incorrectly_lines(self, string: str) -> bool:
        string = ''.join(string.strip().split())
        if not string.isalpha():
            return False
        return all(ord(i) in range(1040, 1104) for i in string)

    def radiate_signal(self) -> None:
        """
        Излучение сиганала, если все данные введены верно.
        """
        self.communicate.signal.emit()

    def get_director(self) -> tuple:
        director_info = tuple(list(map(lambda line: ' '.join(list(map(lambda x: x.capitalize(),
                                                                      line.text().strip().split()))), self.lines)))
        if self.ind >= 0:
            return self.ind, *director_info
        return director_info

    def clear(self) -> None:
        """
        Очистка всех полей и сообщениый при закрытии окна
        """
        for line in self.lines:
            line.setStyleSheet(f'background-color: {self.normal_line_color}')
            line.setText('')
        self.statusBar.showMessage('')
        self.statusBar.setStyleSheet(f'background-color: {self.normal_window_color}')

    def closeEvent(self, event) -> None:
        self.clear()
        self.close()


class SessionSetupWindow(QMainWindow):
    """
    Окно настройки сеанса.
    """
    session_signal = pyqtSignal()

    def __init__(self, window_title: str, date_: tuple, index=-1, hour=8, minute=0, hall=1):
        super().__init__()
        try:
            assert all(isinstance(i, int) for i in date_) and len(date_) == 3
        except AssertionError:
            raise ValueError('Аргумент date_ должен содержать кортедж с 3 целыми числами: год, месяц, день')

        self.window_title = window_title
        self.date_ = date_
        self.ind = index
        self.hour, self.minute, self.hall = hour, minute, hall
        self.statusBar = QStatusBar()

        uic.loadUi('Interfaces\\SessionSetupWindow.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setStatusBar(self.statusBar)
        self.setWindowTitle(self.window_title)

        self.TimeEdit.setTime(QTime(self.hour, self.minute))
        self.SpinBox.setValue(self.hall)

        self.ConfirmSessionBtn.clicked.connect(self.session_signal)

    def get_session(self):
        """
        Возвращает информацию о сеансе
        """
        if self.ind >= 0:
            return self.ind, self.date_,\
                   [self.TimeEdit.time().hour(), self.TimeEdit.time().minute(), self.SpinBox.value()]
        return self.date_, [self.TimeEdit.time().hour(), self.TimeEdit.time().minute(), self.SpinBox.value()]


class Communicate(QObject):
    signal = pyqtSignal()


if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setStyle('Fusion')
    StWin = AdminWindow()
    StWin.show()
    sys.exit(App.exec_())
