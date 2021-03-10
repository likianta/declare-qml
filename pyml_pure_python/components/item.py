from pyml_pure_python.keywords import true
from .base_com import BaseComponent


class Item(BaseComponent):
    enabled: bool
    height: float
    width: float
    
    size: tuple
    
    def _init_raw_props(self):
        self.enabled = true
        self.height = 0
        self.width = 0
    
    def _init_custom_props(self):
        self.size = (0, 0)
    
    def on_size_changed(self, v):
        self.width, self.height = v
    
    def on_width_changed(self, v):
        self.size = (v, self.height)
    
    def on_height_changed(self, v):
        self.size = (self.width, v)
