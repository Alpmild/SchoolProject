import sqlite3 as sql
from datetime import time

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QPixmap
from PyQt5 import uic

from Classes.HallWindow_Ui import HallWindow


class FilmWindow(QMainWindow):
    """
    Окно фильма со всей нужной информацией для пользователя
    """
    def __init__(self, film_info: tuple, genres: tuple, directors: tuple, sessions: list):
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