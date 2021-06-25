from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication


class Application(QApplication):
    
    def __init__(self, **kwargs):
        """
        Args:
            **kwargs:
                organization: str, default 'dev.likianta.declare_qml'.
        """
        super().__init__()
        
        self.engine = QQmlApplicationEngine()
        self.root = self.engine.rootContext()
        
        # set organization name to avoid raising warning info when we use
        # `QtQuick.Dialogs.FileDialog` component
        self.setOrganizationName(kwargs.get(
            'organization', 'dev.likianta.declare_qml'
        ))
        self.set_global_conf()
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def set_global_conf(self):
        # set font 'Microsoft Yahei UI' in Windows if available
        from platform import system
        if system() == 'Windows':
            from PySide6.QtGui import QFont
            self.setFont(QFont('Microsoft YaHei UI'))
    
    # noinspection PyMethodMayBeStatic
    def build(self):  # TODO
        return ''
    
    def start(self, qmlfile: str = 'index.qml'):
        with open(qmlfile, 'w', encoding='utf-8') as f:
            f.write(self.build())
        
        self.engine.load(qmlfile)
        self.exec()
