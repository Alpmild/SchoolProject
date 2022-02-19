from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

from Classes.Consts import TD_INTERFACE


class TabDialog(QDialog):
    """
    Окно с кодом заказа
    """
    def __init__(self, ordered_places: tuple):
        self.parent = None

        self.ordered_places = ordered_places
        super().__init__()
        uic.loadUi(TD_INTERFACE, self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setModal(True)

        ordered_places = '\n'.join([f'Ряд {r + 1} Место {c + 1}' for r, c in self.ordered_places])
        self.PlainTextEdit.setPlainText(f'Ваш уникальный код:\n'
                                        f'{hash(self.ordered_places)}\n'
                                        f'\n'
                                        f'Ваш заказ:\n'
                                        f'{ordered_places}\n'
                                        f'\n'
                                        f'Спасибо за покупку :)')
