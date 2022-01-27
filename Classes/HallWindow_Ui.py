import sqlite3 as sql

from PyQt5.QtWidgets import QMainWindow, QStatusBar
from PyQt5 import uic

from Classes.TabWindow_Ui import TabWindow


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

    def close_the_place(self, row_ind: int, col_ind: int, place_is_taken: bool):
        """
        Красным закрашивуются уже ранее купленный места, а остальные при нажатие добавляются в заказ
        """
        if place_is_taken:
            self.place_btns[row_ind][col_ind].setStyleSheet(f'background-color: {self.occupied_color}')
        else:
            self.place_btns[row_ind][col_ind].clicked.connect(lambda: self.order_place(row_ind, col_ind))

    def order_place(self, row_ind: int, col_ind: int):
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

    def buy_tickets(self):
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