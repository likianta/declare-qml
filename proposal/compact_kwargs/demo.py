from typing import TypedDict
from secrets import token_hex

from lk_logger import lk
from lk_utils import dumps


def _generate_random_key(prefix=''):
    return f'{prefix}_{token_hex(8)}'


class Context:
    on_widget_creation = False


class TypeSheet(TypedDict):
    width: int
    height: int
    ...
    

class Component:
    
    # noinspection PyShadowingBuiltins
    def __init__(self, id=None, **kwargs):
        Context.on_widget_creation = True
        
        self._id = id or ''
        self._children = kwargs.pop('children', [])
        self._kwargs = kwargs
        
        Context.on_widget_creation = False
        
    def compose(self):
        return '''
            {component_name} {{
                {id}
                {object_name}
                
                {properties}
                
                {custom_properties}
                
                {children}
            }}
        '''.format(
            component_name=self.__class__.__name__,
            id=self._id and f'id: {self._id}',
            # object_name=self._id and
            #             f'objectName: {self._id}{_generate_random_key()}',
            object_name='',
            properties='\n'.join(
                '{}: {}'.format(self.convert_name_case(k),
                                self.convert_value_type(v))
                for k, v in self._kwargs.items()
            ),
            custom_properties='',
            children='\n'.join(x.compose() for x in self._children)
        )
    
    @staticmethod
    def convert_name_case(raw_name: str):
        def _convert_case(name: str):
            words = name.split('_')
            return words[0] + ''.join(x.title() for x in words[1:])

        segs = raw_name.split('__')
        return '.'.join(map(_convert_case, segs))

    @staticmethod
    def convert_value_type(value):
        if type(value) is str:
            if value.startswith('wid_'):
                return value
            else:
                return f'"{value}"'
        if type(value) is bool:
            return 'true' if value else 'false'
        else:
            return str(value)


class Application:
    
    def __init__(self, app_name: str, window: Component):
        self.app_name = app_name
        self.window = window
        self.start()
        
    def start(self):
        dumps(self.window.compose(), 'index.qml')
        lk.loga('index.qml')


class Window(Component):
    pass


class Image(Component):
    pass


class References:
    _refs = {}
    
    def __getattr__(self, item) -> str:
        if Context.on_widget_creation:
            return self.new(item)
        else:
            return self._refs[item]
    
    def __setattr__(self, key, value):
        self.new(key, value)
    
    def new(self, name, value=None):
        assert name not in self._refs
        self._refs[name] = value or _generate_random_key('wid')
        return name
    
    
class Property:

    def __init__(self, name):
        self.name = name

    def __getattr__(self, item) -> str:
        return f'{self.name}.{item}'


refs = References()
if True:
    refs.win = None
    refs.img = None

app = Application(
    app_name='Demo App',
    window=Window(
        id=refs.win,
        width=600,
        height=460,
        color='#F2F2F2',
        visible=True,
        children=[
            Image(
                id=refs.img,
                anchors__center_in=refs.win,
                rotation=0,
                source='windmill.png',
                visible=True,
            )
        ]
    )
)
