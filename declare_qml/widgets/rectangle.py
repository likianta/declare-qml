from .item import Item


class Rectangle(Item):
    _sup_props = Item._own_props
    _own_props = ['color', 'radius']
    _new_props = []
    
    def __init__(self):
        super().__init__()
        
        self.color = '#ffffff'
        self.radius = 0
