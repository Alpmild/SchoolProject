from PyQt5.QtWidgets import QDialog, QPushButton
from PyQt5 import uic

from data.TabDialog import TabDialog
from data.Consts import (PROJECT_DATABASE, HD_INTERFACE, OCCUPIED_COLOR,
                            NORMAL_WINDOW_COLOR, MAX_BUY_PLACES, ORDER_COLOR)

import sqlite3 as sql


class HallDialog(QDialog):
    """
    Окно зала, которое получает session_id для записи покупкт билетов
    """
    def __init__(self, session_id: int, title: str):
        super().__init__()
        self.parent = None

        self.session_id = session_id
        self.title = title

        self.projectDB = sql.connect(PROJECT_DATABASE)
        self.projectDB_cur = self.projectDB.cursor()

        self.tab_window = None
        uic.loadUi(HD_INTERFACE, self)
        self.place_buttons = [
            (self.Btn00, self.Btn01, self.Btn02, self.Btn03, self.Btn04, self.Btn05, self.Btn06, self.Btn07, self.Btn08,
             self.Btn09),
            (self.Btn10, self.Btn11, self.Btn12, self.Btn13, self.Btn14, self.Btn15, self.Btn16, self.Btn17, self.Btn18,
             self.Btn19, self.Btn110, self.Btn111),
            (self.Btn30, self.Btn31, self.Btn32, self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38,
             self.Btn39, self.Btn310, self.Btn311, self.Btn312, self.Btn313),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213),
            (self.Btn30, self.Btn31, self.Btn32, self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38,
             self.Btn39, self.Btn310, self.Btn311, self.Btn312, self.Btn313),
            (self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44, self.Btn45, self.Btn46, self.Btn47, self.Btn48,
             self.Btn49, self.Btn410, self.Btn411, self.Btn412, self.Btn413),
            (self.Btn50, self.Btn51, self.Btn52, self.Btn53, self.Btn54, self.Btn55, self.Btn56, self.Btn57, self.Btn58,
             self.Btn59, self.Btn510, self.Btn511, self.Btn512, self.Btn513),
            (self.Btn60, self.Btn61, self.Btn62, self.Btn63, self.Btn64, self.Btn65, self.Btn66, self.Btn67, self.Btn68,
             self.Btn69, self.Btn610, self.Btn611, self.Btn612, self.Btn613),
            (self.Btn70, self.Btn71, self.Btn72, self.Btn73, self.Btn74, self.Btn75, self.Btn76, self.Btn77, self.Btn78,
             self.Btn79, self.Btn710, self.Btn711, self.Btn712, self.Btn713),
            (self.Btn80, self.Btn81, self.Btn82, self.Btn83, self.Btn84, self.Btn85, self.Btn86, self.Btn87, self.Btn88,
             self.Btn89, self.Btn810, self.Btn811, self.Btn812, self.Btn813)
        ]
        self.ordered_places = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'Купить билеты на фильм "{self.title}"')
        self.setFixedSize(self.size())
        self.setModal(True)

        purchased_seats = self.projectDB_cur.execute("SELECT row, column FROM Tickets WHERE session_id = ?",
                                                     (self.session_id,)).fetchall()
        for row, buttons_list in enumerate(self.place_buttons):
            for col, button in enumerate(buttons_list):
                self.close_the_place(button, row, col, (row, col) in purchased_seats)

        self.set_btn_status()
        self.BuyBtn.clicked.connect(self.buy_tickets)

    def set_btn_status(self):
        self.BuyBtn.setEnabled(bool(self.ordered_places))

    def close_the_place(self, button: QPushButton, row: int, col: int, place_is_taken: bool):
        """
        Красным закрашивуются уже ранее купленный места, а остальные при нажатие добавляются в заказ
        """
        if place_is_taken:
            button.setStyleSheet(f'background-color: {OCCUPIED_COLOR}')
        else:
            button.clicked.connect(lambda: self.order_place(row, col))

    def order_place(self, row: int, col: int):
        """
        Добавление заказываемых пользователей мест в список
        """
        if (row, col) in self.ordered_places:
            self.ordered_places.remove((row, col))
            self.place_buttons[row][col].setStyleSheet(f'background-color: {NORMAL_WINDOW_COLOR}')
        else:
            if len(self.ordered_places) < MAX_BUY_PLACES:
                self.ordered_places.append((row, col))
                self.place_buttons[row][col].setStyleSheet(f'background-color: {ORDER_COLOR}')
        print(self.ordered_places)

        self.set_btn_status()

    def buy_tickets(self):
        """
        Покупка билетов и добавление заказанных мест в базу
        """
        insert_places = f"INSERT INTO Tickets VALUES({self.session_id}, ?, ?)"
        for row, col in self.ordered_places:
            self.projectDB_cur.execute(insert_places, (row, col))
            self.projectDB.commit()

        self.tab_window = TabDialog(tuple(self.ordered_places))
        self.tab_window.show()

        self.close()
