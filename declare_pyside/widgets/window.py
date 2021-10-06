from declare_foundation.context_manager import Context
from .base_item import BaseItem

_is_main_window = True
_curr_dir = f'{__file__}/..'


class Window(Context):
    
    def __init__(self):
        super().__init__()
        
        global _is_main_window
        if _is_main_window:
            self.qmlfile = f'{_curr_dir}/qml_assets/MainWindow.qml'
            _is_main_window = False
        else:
            self.qmlfile = f'{_curr_dir}/qml_assets/Window.qml'
    
    # def __enter__(self):
    #     Context.__enter__(self)
    #     return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from ..pyside import app
        app.start(self.qmlfile)
