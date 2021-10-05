from ...typehint import Any


class Property:
    is_static: bool
    qtype: str
    value: Any
    
    def __init__(self, pyval):
        self.value = pyval
    
    def adapt(self) -> str:
        """ adapt value to qml recognizable type. """
        raise NotImplementedError


class PyFunc(Property):
    
    def adapt(self):
        return f'PySide.call()'
