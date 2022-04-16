from datetime import date

from PyQt5.QtWidgets import QMainWindow, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from data.Consts import PROJECT_DATABASE, FW_INTERFACE, GENRES_DICT, MAX_SESSIONS
from data.HallDialog import HallDialog

import sqlite3 as sql


class FilmWindow(QMainWindow):
    """
    Окно фильма со всей нужной информацией для пользователя
    """

    def __init__(self, film_info: dict, date_: date):
        super().__init__()
        self.film_info = film_info
        self.selected_date = date_

        self.HallWindow = None

        self.projectDB = sql.connect(PROJECT_DATABASE)
        self.projectDB_cur = self.projectDB.cursor()

        uic.loadUi(FW_INTERFACE, self)
        self.info_lines = (self.NameLine, self.CountryLine, self.GenresLine,
                           self.AgeRatingLine, self.DurationLine)
        self.session_buttons = (self.Session0Btn, self.Session1Btn, self.Session2Btn, self.Session3Btn,
                                self.Session4Btn, self.Session5Btn, self.Session6Btn, self.Session7Btn)
        self.setFixedSize(self.size())
        self.init_ui()

    def init_ui(self):
        """
        Загрузка информации о фильме в окно
        """
        (film_id, title, country, rating, duration, genres, directors, sessions,
         file_folder_name, description_file_name, image_name) = (self.film_info['film_id'],
                                                                 self.film_info['title'],
                                                                 self.film_info['country'],
                                                                 str(self.film_info['rating']),
                                                                 self.film_info['duration'],
                                                                 self.film_info['genres'],
                                                                 self.film_info['directors'],
                                                                 self.film_info['sessions'][self.selected_date],
                                                                 self.film_info['file_folder_name'],
                                                                 self.film_info['description_file_name'],
                                                                 self.film_info['image_path'])

        self.setWindowTitle(title)

        genres = ', '.join(map(lambda i_: GENRES_DICT[i_], genres)).capitalize()
        directors = ', '.join(list(map(lambda i_: ' '.join(i_), directors)))

        hours_dur, minutes_dur = divmod(duration, 60)
        if hours_dur > 0 and minutes_dur > 0:
            duration = f'{hours_dur}ч. {minutes_dur}мин.'
        elif hours_dur > 0 and minutes_dur == 0:
            duration = f'{hours_dur}ч.'
        else:
            duration = f'{minutes_dur}мин.'

        description_text = ''
        try:
            with open(description_file_name, 'r') as description_file:
                description_text = description_file.read().replace('\n', ' ')
        except FileNotFoundError:
            pass

        # Заполнение полей с информацией о фильме
        info = (title, country, genres, f'{rating}+', duration)
        for i, line in enumerate(self.info_lines):
            line.setText(info[i])

        self.DirectorsPlainText.setPlainText(directors)
        self.DescriptionPlainText.setPlainText(description_text)

        self.ImageLabel.setPixmap(QPixmap(image_name))

        # Заполнение сеансов
        limit = min(MAX_SESSIONS, len(sessions))

        for btn in self.session_buttons[limit:]:
            btn.hide()
        self.session_buttons = self.session_buttons[:limit]

        for i, btn in enumerate(self.session_buttons):
            btn.setText(f'{sessions[i][1].strftime("%H:%M")}\nЗал {sessions[i][2]}')
            self.bind_btn(btn, sessions[i][0])

    def bind_btn(self, btn: QPushButton, session_id: int):
        """
        Назначение на каждую кнопку определенного сеанса
        """
        btn.clicked.connect(lambda: self.open_order_menu(session_id))

    def open_order_menu(self, session_id: int):  # Открывается окно зала для выбора места
        self.HallWindow = HallDialog(session_id, self.film_info['title'])
        self.HallWindow.show()

    def closeEvent(self, event):
        try:
            self.HallWindow.close()
        except AttributeError:
            pass
        self.close()
