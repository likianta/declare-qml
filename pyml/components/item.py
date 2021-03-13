from pyml.core.property import Anchors
from pyml.keywords import true
from .base_component import BaseComponent


class Item(BaseComponent):
    anchors: Anchors
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
    
    @property
    def left(self):
        return self.uid
    
    @property
    def right(self):
        return self.uid
    
    @property
    def top(self):
        return self.uid
    
    @property
    def bottom(self):
        return self.uid
    
    @property
    def hcenter(self):
        return self.uid
    
    @property
    def vcenter(self):
        return self.uid
