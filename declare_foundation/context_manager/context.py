from .dict_tree import DictTreeEx
from .keywords import parent, this
from .uid_system import id_ref


class Context:
    # component tree
    _tree = DictTreeEx(
        {'uid': None, 'level': 0, 'com': None, 'children': {}},
        setin='children'
    )
    ''' {
            uid: {
                'uid': `uid_system.UID|None`,
                'level': `int 0|1|2|3|...`,
                'com': `comonents/base_component.py:BaseComponent`,
                'children': {
                    uid: {
                        'uid': ...,
                        'level': ...,
                        'com': ...,
                        'children': { ... }
                    }, ...
                }
            }, ...
        }
    '''
    
    def update(self, uid, layer_level, com, last_com):
        """
        Returns:
            (this, parent)
        """
        parent_id = str(uid.parent_id)
        uid = str(uid)
        
        kwargs = {'uid': uid, 'level': layer_level, 'com': com}
        
        curr_level = layer_level
        last_level = last_com.level if last_com else -1
        
        if curr_level > last_level:
            self._tree.insert_inside(uid, **kwargs)
        elif curr_level == last_level:
            self._tree.insert_beside(uid, **kwargs)
        else:
            if (dedent_count := last_level - curr_level) == 1:
                self._tree.insert_ouside(uid, **kwargs)
            else:
                # noinspection PyTypeChecker
                for key in ([None] * (dedent_count - 1) + [uid]):
                    self._tree.insert_ouside(key)
        
        # ----------------------------------------------------------------------
        # update `id_ref`, `this` and `parent` pointers
        
        this_com = id_ref[uid] = com
        parent_com = id_ref[parent_id]
        
        this.point_to(this_com)
        parent.point_to(parent_com)
        
        return this, parent


context = Context()
