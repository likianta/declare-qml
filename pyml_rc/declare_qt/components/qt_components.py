from PySide6.QtWidgets import QLabel, QMainWindow

from .base_component import BaseComponent


class MainWindow(QMainWindow, BaseComponent):
    pass


class Label(QLabel, BaseComponent):
    pass
