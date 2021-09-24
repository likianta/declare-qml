from typing import *

if __name__ == '__main__':
    from declare_foundation.components import BaseComponent as _Component
else:
    _Component = None

# ------------------------------------------------------------------------------

TComponent = _Component

# TComponentID = Union[TComponent, str]
# TComponentNo = int  # int >= 1

TProperties = dict
TPyVal = Any  # 'Python Value'


class _Final:
    """
    Constable type.
    
    Constable[X] is equivalent to Union[X, Constable].
    """
    
    def __getitem__(self, item):
        from .keywords.keywords import Const
        return Union[item, Const]


TFinal = _Final()
