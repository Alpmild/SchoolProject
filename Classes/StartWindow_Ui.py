from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

from Classes.LoginWindow_Ui import LoginWindow
from Classes.UserWindow_Ui import UserWindow


class StartWindow(QMainWindow):
    """
    Стартовое окно
    """
    def __init__(self):
        super(QMainWindow, self).__init__()
        uic.loadUi('Interfaces\\StartWindow.ui', self)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(self.size())
        self.setWindowTitle('Стартовое окно приложения')
        self.UserLoginBtn.clicked.connect(self.open_user_window)
        self.AdminLoginBtn.clicked.connect(self.open_login_window)

    def open_user_window(self):
        """
        Человек сразу заходит в приложение и начинает им пользоваться
        """
        self.UserWin = UserWindow()
        self.UserWin.show()
        self.close()

    def open_login_window(self):
        """
        Открывается окно подтверждения -> LoginWindow
        """
        self.LgnWin = LoginWindow()
        self.LgnWin.show()
        self.close()
