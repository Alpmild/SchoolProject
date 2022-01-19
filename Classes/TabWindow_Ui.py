from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic


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