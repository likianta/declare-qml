from pyml_pure_python._typing_hint import *
from .struct import StructEx


class Context:
    # DEL
    _index = 0
    _layers = [[]]  # type: list[list]
    _layer = _layers[_index]  # type: list
    
    _com_tree = StructEx(
        {'uid': '', 'level': 0, 'com': None, 'children': {}},
        setin='children'
    )
    ''' {
            uid: {
                'uid': uid,
                'level': 0,
                'com': com,
                'children': {
                    uid: {...},
                    ...
                }
            },
            ...
        }
    '''
    
    def update(self, uid: TComponentID, layer_level: TLayerLevel,
               com: TComponent, last_com: TRepresents):
        """
        
        Args:
            uid:
            layer_level:
            com:
            last_com:

        Returns:
            (this, parent)
        """
        kwargs = {'uid': uid, 'level': layer_level, 'com': com}
        
        curr_level = layer_level
        last_level = last_com.level if last_com else -1
        
        if curr_level > last_level:
            self._com_tree.insert_inside(uid, **kwargs)
        elif curr_level == last_level:
            self._com_tree.insert_beside(uid, **kwargs)
        else:
            if (dedent_count := last_level - curr_level) == 1:
                self._com_tree.insert_ouside(uid, **kwargs)
            else:
                # noinspection PyTypeChecker
                for key in ([None] * (dedent_count - 1) + [uid]):
                    self._com_tree.insert_ouside(key)

        # ----------------------------------------------------------------------

        from pyml_pure_python.core import id_ref, id_gen
        this_com = id_ref[uid] = com
        parent_com = id_ref[id_gen.get_parent_id(uid)]
        
        # FIXME: 相互指认关系的行为是否合适?
        this_com.parent = parent_com
        if parent_com: parent_com.children.append(this_com)

        # try:
        #     # noinspection PyProtectedMember
        #     this_com, parent_com = com, self._com_tree._last_node['com']
        #     this_com.parent = parent_com
        #     parent_com.children.append(this_com)
        # except AttributeError:
        #     this_com, parent_com = com, None
        
        from pyml_pure_python.keywords import this, parent
        this.point_to(this_com)
        parent.point_to(parent_com)
        return this, parent
    
    def add_layer(self):
        self._layers.append([])
        self._index += 1
        self._layer = self._layers[self._index]
        # # self._layer = self._layers[-1]
    
    def append(self, obj):
        self._layer.append(obj)
    
    def backwards(self):
        self._index -= 1
        self._layer = self._layers[self._index]
    
    def __len__(self):
        return len(self._layer)


class Property:
    _deliver: list
    
    def __init__(self):
        pass
    
    def __setattr__(self, key, value):
        self.__dict__[key] = value
        
        if (on_key := f'on_{key}') not in self.__dict__:
            self.__dict__[on_key] = Signal(self._deliver)
    
    def _on_prop_changed(self, prop, value):
        pass


class Signal:
    
    def __init__(self, _deliver):
        self.slots = set()
        self._deliver = _deliver
    
    def __call__(self, *args, **kwargs):
        """
        Examples:
            # assume button.clicked is an instance of Signal
            button.clicked()
        """
        for f in self.slots:
            f(*self._deliver, *args, **kwargs)
    
    def binding(self, func):
        """
        Examples:
            # assume button.clicked is an instance of Signal
            button.clicked.binding(lambda : print('button is clicked'))
        """
        self.slots.add(func)


# class Compose:
#
#     def build(self):
#         pass
#
#     def __enter__(self):
#         context.append(self)
#         this.represents(self)
#         this.index = len(context)
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         parent.represents(self)
#
#
# class Component(Compose):
#
#     def __init__(self, **kwargs):
#         self.apply(**kwargs)
#
#     def apply(self, width, height):
#         pass
#
#     def on_completed(self):
#         pass

context = Context()
