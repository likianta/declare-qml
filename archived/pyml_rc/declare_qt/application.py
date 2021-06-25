from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


class Application(QApplication):
    
    def __init__(self, app_name=''):
        super(Application, self).__init__()
        if app_name: self.setApplicationName(app_name)
        self.setFont(QFont('Microsoft YaHei UI'))
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.start()
    
    def start(self):
        from sys import exit
        exit(self.exec_())
