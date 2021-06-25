from typing import *

TClassName = str  # e.g. 'Item', 'Rectangle', 'MouseArea', ...
TModuleName = str
TPackageName = str  # e.g. 'QtQuick.Controls'

TProperty = str  # e.g. 'border', 'border.color', 'width', 'height', ...

TQType = Literal['array', 'bool', 'color', 'group', 'int', 'real', 'string',
                 'var']
TQmlType = str

# ------------------------------------------------------------------------------

TDataNo5 = dict[TModuleName, dict[TQmlType, ]]
'''
    {
        module: {
            qmltype: {
                'parent': parent_qmltype,
                'props': {prop: type, ...}
            }, ...
        }, ...
    }
'''


class _TDataNo6Value(TypedDict):
    parent: TClassName
    props: dict[TProperty, TQType]


TDataNo6 = dict[TPackageName, dict[TClassName, _TDataNo6Value]]
'''
    {
        TPackageName: {
            TClassName: {
                'parent': TClassName,
                'props': {TProperty: TQType, ...}
            }, ...
        }, ...
    }
    e.g. {
        'qtquick': {
            'Rectangle': {
                'parent': 'Item',
                'props': {
                    'border': 'group',
                    'border.color': 'color',
                    ...
                }
            }, ...
        }, ...
    }
'''
