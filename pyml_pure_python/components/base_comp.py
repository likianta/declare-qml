# noinspection PyProtectedMember
from sys import _getframe

from pyml_pure_python.core import context
from pyml_pure_python.keywords import this


class BaseComponent:
    name: str
    
    _initialized = False
    _propagating = False
    _propagations: set
    _props: dict
    
    def __init__(self):
        self._propagations = set()
        self._props = {
            'raw_props'   : [],
            'custom_props': [],
        }
        self._init_raw_props()
        self._init_custom_props()
        self.name = self.__class__.__name__
        self._initialized = True
    
    def _init_raw_props(self):
        raise NotImplementedError
    
    def _init_custom_props(self):
        pass
    
    def __getattr__(self, item):
        if (
                isinstance(item, str) and
                item.startswith('on_') and
                item.endswith('_changed')
        ):
            return self.__dict__.get(item, lambda v: v)
        else:
            return self.__dict__[item]
    
    def __setattr__(self, key, value, propagate=True):
        # https://www.cnblogs.com/hester/articles/4767152.html
        caller_name = _getframe(1).f_code.co_name  # type: str
        
        if self._initialized:
            if (
                    caller_name.startswith('on_') and
                    caller_name.endswith('_changed')
            ):
                if key in self._propagations:
                    return
            else:
                self._propagations.clear()
            self._propagations.add(key)
        
        super().__setattr__(key, value)
        
        if self._initialized is False:
            if caller_name == '_init_raw_props':
                self._props['raw_props'].append(key)
            elif caller_name == '_init_custom_props':
                self._props['custom_props'].append(key)
        else:
            getattr(self, f'on_{key}_changed', lambda v: v)(value)
    
    def __enter__(self):
        """
        with BaseComponent() as comp:
            #   1. update `this` indicates to `comp`
            #   2. update `context` surrounds `comp`
            ...
        """
        context.append(self)
        this.represents(self)
        this.index = len(context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        this.represents(this.parent)
    
    def build(self):
        from textwrap import dedent
        return dedent('''
            {component} {{
                {body}
            }}
        '''.format(
            component=self.name,
            body=('\n' + ' ' * 16).join(self.properties)
        ))
    
    @property
    def properties(self):
        out = [f'objectName: {self.name}']
        
        for k in self._props['raw_props']:
            v = getattr(self, k)
            
            if isinstance(v, BaseComponent):
                out.append(v.build())
            else:
                out.append(f'{name_2_camel_case(k)}: {getattr(self, k)}')
        
        return out


def name_2_camel_case(name: str):
    segs = name.split('_')
    return segs[0] + ''.join(x.title() for x in segs[1:])
