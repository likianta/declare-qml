from ..item import Item


class Window(Item):
    _sup_props = Item._own_props
    _own_props = ['color', 'visible']
    _new_props = []
    
    def __init__(self):
        super().__init__()
        
        self.color = '#ffffff'
        self.visible = True
