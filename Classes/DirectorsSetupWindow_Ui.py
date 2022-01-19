from PyQt5.QtWidgets import QMainWindow, QStatusBar
from PyQt5 import uic

from Classes.Communicate import Communicate
from Classes.Consts import *


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
                self.lines[i].setStyleSheet(f'background-color: {ERROR_COLOR}')
                self.lines[i].setText('')
            if len(indexes) == 1:
                self.statusBar.showMessage(self.bool_error_messages[indexes[0]])
            else:
                self.statusBar.showMessage(self.bool_error_messages[2])
            self.statusBar.setStyleSheet(f'background-color: {ERROR_COLOR}')
            return

        flag = True
        person_info = tuple(' '.join(line.text().strip().split()) for line in self.lines)
        for i in range(len(person_info)):
            if not self.indication_incorrectly_lines(person_info[i]):
                flag = False
                self.lines[i].setStyleSheet(f'background-color: {ERROR_COLOR}')

        if flag:
            self.radiate_signal()
        else:
            self.statusBar.setStyleSheet(f'background-color: {ERROR_COLOR}')
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