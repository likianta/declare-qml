from declare_foundation.typehint import *

# TComponentID = Union[TComponent, str]
# TComponentNo = int  # int >= 1

TProperties = dict
TPyVal = Any  # 'Python Value'


class _Constable:
    """
    Constable type.
    
    Constable[X] is equivalent to Union[X, Constable].
    """
    
    def __getitem__(self, item):
        from pyml.keywords.keywords import Const
        return Union[item, Const]


TConstable = _Constable()
