from .generic import Property


class IntProperty(Property):
    is_static = True
    qtype = 'int'
    
    def adapt(self) -> str:
        return str(self.value)


class FloatProperty(Property):
    is_static = True
    qtype = 'real'
    
    def adapt(self) -> str:
        return str(self.value)


class BoolProperty(Property):
    is_static = True
    qtype = 'bool'
    
    def adapt(self) -> str:
        return 'true' if self.value else 'false'


class StringProperty(Property):
    is_static = True
    qtype = 'string'
    
    def adapt(self) -> str:
        value = self.value.replace('"', '\\"')
        return f'"{value}"'


class VarProperty(Property):
    is_static = False
    qtype = 'var'
    
    def adapt(self) -> str:
        return str(self.value)
