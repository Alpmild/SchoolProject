from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5 import uic

from Classes.TabWindow_Ui import TabWindow
from Classes.Consts import *

import sqlite3 as sql


class HallWindow(QDialog):
    """
    Окно зала, которое получает session_id для записи покупкт билетов
    """

    def __init__(self, session_id: int):
        super(HallWindow, self).__init__()
        uic.loadUi('Interfaces\\HallDialog.ui')

        self.buttons = [
            (self.Btn00, self.Btn01, self.Btn02, self.Btn03, self.Btn04, self.Btn05, self.Btn06, self.Btn07, self.Btn08,
             self.Btn09),
            (self.Btn10, self.Btn11, self.Btn12, self.Btn13, self.Btn14, self.Btn15, self.Btn16, self.Btn17, self.Btn18,
             self.Btn19, self.Btn110, self.Btn111), (
                self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27,
                self.Btn28,
                self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313, self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44,
             self.Btn45, self.Btn46, self.Btn47, self.Btn48, self.Btn49, self.Btn410, self.Btn411, self.Btn412,
             self.Btn413),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313, self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44,
             self.Btn45, self.Btn46, self.Btn47, self.Btn48, self.Btn49, self.Btn410, self.Btn411, self.Btn412,
             self.Btn413, self.Btn50, self.Btn51, self.Btn52, self.Btn53, self.Btn54, self.Btn55, self.Btn56,
             self.Btn57, self.Btn58, self.Btn59, self.Btn510, self.Btn511, self.Btn512, self.Btn513),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313, self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44,
             self.Btn45, self.Btn46, self.Btn47, self.Btn48, self.Btn49, self.Btn410, self.Btn411, self.Btn412,
             self.Btn413, self.Btn50, self.Btn51, self.Btn52, self.Btn53, self.Btn54, self.Btn55, self.Btn56,
             self.Btn57, self.Btn58, self.Btn59, self.Btn510, self.Btn511, self.Btn512, self.Btn513, self.Btn60,
             self.Btn61, self.Btn62, self.Btn63, self.Btn64, self.Btn65, self.Btn66, self.Btn67, self.Btn68, self.Btn69,
             self.Btn610, self.Btn611, self.Btn612, self.Btn613),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313, self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44,
             self.Btn45, self.Btn46, self.Btn47, self.Btn48, self.Btn49, self.Btn410, self.Btn411, self.Btn412,
             self.Btn413, self.Btn50, self.Btn51, self.Btn52, self.Btn53, self.Btn54, self.Btn55, self.Btn56,
             self.Btn57, self.Btn58, self.Btn59, self.Btn510, self.Btn511, self.Btn512, self.Btn513, self.Btn60,
             self.Btn61, self.Btn62, self.Btn63, self.Btn64, self.Btn65, self.Btn66, self.Btn67, self.Btn68, self.Btn69,
             self.Btn610, self.Btn611, self.Btn612, self.Btn613, self.Btn70, self.Btn71, self.Btn72, self.Btn73,
             self.Btn74, self.Btn75, self.Btn76, self.Btn77, self.Btn78, self.Btn79, self.Btn710, self.Btn711,
             self.Btn712, self.Btn713),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313, self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44,
             self.Btn45, self.Btn46, self.Btn47, self.Btn48, self.Btn49, self.Btn410, self.Btn411, self.Btn412,
             self.Btn413, self.Btn50, self.Btn51, self.Btn52, self.Btn53, self.Btn54, self.Btn55, self.Btn56,
             self.Btn57, self.Btn58, self.Btn59, self.Btn510, self.Btn511, self.Btn512, self.Btn513, self.Btn60,
             self.Btn61, self.Btn62, self.Btn63, self.Btn64, self.Btn65, self.Btn66, self.Btn67, self.Btn68, self.Btn69,
             self.Btn610, self.Btn611, self.Btn612, self.Btn613, self.Btn70, self.Btn71, self.Btn72, self.Btn73,
             self.Btn74, self.Btn75, self.Btn76, self.Btn77, self.Btn78, self.Btn79, self.Btn710, self.Btn711,
             self.Btn712, self.Btn713, self.Btn80, self.Btn81, self.Btn82, self.Btn83, self.Btn84, self.Btn85,
             self.Btn86, self.Btn87, self.Btn88, self.Btn89, self.Btn810, self.Btn811, self.Btn812, self.Btn813),
            (self.Btn20, self.Btn21, self.Btn22, self.Btn23, self.Btn24, self.Btn25, self.Btn26, self.Btn27, self.Btn28,
             self.Btn29, self.Btn210, self.Btn211, self.Btn212, self.Btn213, self.Btn30, self.Btn31, self.Btn32,
             self.Btn33, self.Btn34, self.Btn35, self.Btn36, self.Btn37, self.Btn38, self.Btn39, self.Btn310,
             self.Btn311, self.Btn312, self.Btn313, self.Btn40, self.Btn41, self.Btn42, self.Btn43, self.Btn44,
             self.Btn45, self.Btn46, self.Btn47, self.Btn48, self.Btn49, self.Btn410, self.Btn411, self.Btn412,
             self.Btn413, self.Btn50, self.Btn51, self.Btn52, self.Btn53, self.Btn54, self.Btn55, self.Btn56,
             self.Btn57, self.Btn58, self.Btn59, self.Btn510, self.Btn511, self.Btn512, self.Btn513, self.Btn60,
             self.Btn61, self.Btn62, self.Btn63, self.Btn64, self.Btn65, self.Btn66, self.Btn67, self.Btn68, self.Btn69,
             self.Btn610, self.Btn611, self.Btn612, self.Btn613, self.Btn70, self.Btn71, self.Btn72, self.Btn73,
             self.Btn74, self.Btn75, self.Btn76, self.Btn77, self.Btn78, self.Btn79, self.Btn710, self.Btn711,
             self.Btn712, self.Btn713, self.Btn80, self.Btn81, self.Btn82, self.Btn83, self.Btn84, self.Btn85,
             self.Btn86, self.Btn87, self.Btn88, self.Btn89, self.Btn810, self.Btn811, self.Btn812, self.Btn813,
             self.Btn90, self.Btn91, self.Btn92, self.Btn93, self.Btn94, self.Btn95, self.Btn96, self.Btn97, self.Btn98,
             self.Btn99, self.Btn910, self.Btn911, self.Btn912, self.Btn913)
        ]


s = 'self.Btn'
btns = []
for i in range(2, 10):
    n = s + str(i)
    for j in range(14):
        btns.append(n + str(j))
    print(f'({", ".join(btns)}),')
    btns = []

h = HallWindow(33)
