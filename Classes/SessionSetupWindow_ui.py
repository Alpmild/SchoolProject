from PyQt5.QtCore import pyqtSignal

from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QMainWindow, QStatusBar
from PyQt5 import uic


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