from declare_foundation.context_manager import Context
from .base_item import BaseItem
from .core.authorized_props import WindowProps
from ..path_model import widgets_dir

_is_main_window = True


class Window(BaseItem, Context, WindowProps):
    
    def __init__(self):
        Context.__init__(self)
        WindowProps.__init__(self)
        
        global _is_main_window
        if _is_main_window:
            self.qmlfile = f'{widgets_dir}/qml_assets/MainWindow.qml'
            _is_main_window = False
        else:
            self.qmlfile = f'{widgets_dir}/qml_assets/Window.qml'
    
    def __enter__(self):
        Context.__enter__(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        from ..pyside import app
        app.start(self.qmlfile)
