from ..typehint import TProperties, TPyVal


class PropertyManager:
    
    _sup_props = []
    _own_props = []
    _new_props = []
    
    def __init__(self, auto_create_new_prop=False):
        self._auto_create_new_prop = auto_create_new_prop
    
    @property
    def all_props(self) -> TProperties:
        return {k: getattr(self, k) for k in
                self._sup_props + self._own_props + self._new_props}
    
    # note: `raw_props` versus `new_props`, `sup_props` versus `own_props`
    
    @property
    def raw_props(self) -> TProperties:
        return {k: getattr(self, k) for k in
                self._sup_props + self._own_props}
    
    @property
    def new_props(self) -> TProperties:
        return {k: getattr(self, k) for k in
                self._new_props}
    
    @property
    def sup_props(self) -> TProperties:
        return {k: getattr(self, k) for k in
                self._sup_props}
    
    @property
    def own_props(self) -> TProperties:
        return {k: getattr(self, k) for k in
                self._own_props}
    
    def new(self, name: str, value):
        self._new_props.append(name)
        setattr(self, name, value)
    
    # def __setattr__(self, key, value):
    #     if self._auto_create_new_prop and key not in vars(self):
    #         self._new_props[key] = value
    #     else:
    #         super().__setattr__(key, value)


def adapt_key(name: str):
    # e.g. 'background_color' -> 'backgroundColor'
    segs = name.split('_')
    return segs[0] + ''.join(x.title() for x in segs[1:])


def adapt_value(pyval: TPyVal):
    from .types.pyfunc import PyFunc

    if isinstance(pyval, bool):
        # we must put boolean check ahead of int check, cuz `isinstance(True,
        # (int))` would returns True, that's not our expectation.
        return 'true' if pyval else 'false'
    elif isinstance(pyval, (int, float)):
        return str(pyval)
    elif pyval is None:
        return 'null'
    elif isinstance(pyval, str):
        pyval = pyval.replace('"', '\\"')
        return f'"{pyval}"'
    elif isinstance(pyval, PyFunc):
        return pyval.adapt()
    else:
        return str(pyval)
