import sqlite3 as sql

from PyQt5.QtWidgets import QMainWindow, QStatusBar, QLineEdit
from PyQt5 import uic

from Classes.AdminWindow_Ui import AdminWindow
from Classes.Consts import *


class LoginWindow(QMainWindow):
    """
    Окно входа в аккаунт папы-админа :)
    """
    def __init__(self):
        super().__init__()
        self.projectDB = sql.connect('DataBases\\ProjectDataBase.sqlite')
        self.projectDB_cur = self.projectDB.cursor()

        self.ERROR_COLOR = '#ff5133'
        self.statusBar = QStatusBar()
        uic.loadUi('Interfaces\\LoginWindow.ui', self)
        self.init_ui()

    def init_ui(self) -> None:
        self.setFixedSize(self.size())
        self.setWindowTitle('Вход в систему')

        self.ComeInBtn.clicked.connect(self.come_in_press)
        self.CancelBtn.clicked.connect(self.cancel_press)

        self.LoginLine.textChanged.connect(self.hide_error_message)
        self.PasswordLine.textChanged.connect(self.hide_error_message)
        self.PasswordLine.setEchoMode(QLineEdit.Password)

    def hide_error_message(self) -> None:
        self.statusBar.showMessage('')
        self.statusBar.setStyleSheet(f'background-color: {NORMAL_WINDOW_COLOR}')

    def come_in_press(self) -> None:
        """
        Проверка данных для входа в систему
        """
        login, password = self.LoginLine.text(), self.PasswordLine.text()
        if not login or not password:
            return

        try:
            correct_password = self.projectDB_cur.execute(
                "SELECT password FROM Admins_data WHERE login = ?", (login,)).fetchone()[0]
        except TypeError:
            self.show_error()
            return

        if password != str(correct_password):
            self.show_error()
            return
        self.open_admin_window()

    def show_error(self) -> None:
        """
        Показывает сообщение о неправильно введенных данных
        """
        self.statusBar.setStyleSheet(f'background-color: {ERROR_COLOR}')
        self.statusBar.showMessage('Неапрвильно введен логин или пароль.')

    def open_admin_window(self) -> None:
        """
        Открывается основное окно админа
        """
        self.AdminWindow = AdminWindow()
        self.AdminWindow.show()
        self.cancel_press()

    def cancel_press(self) -> None:
        self.close()