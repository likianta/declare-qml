"""
References:
    blueprint/resources/template.txt
"""
from textwrap import dedent
from typing import *

from lk_logger import lk
from lk_utils.read_and_write import dumps, loads


class TypeHint:
    DataR = dict[
        str, dict[
            str, TypedDict(
                'PropValue', {'parent': str, 'props': dict[str, str]})]]


def create_package_dirs(data: TypeHint.DataR):
    # data: from `loads('../resources/no6_all_pyml_widgets.json')`
    from os import mkdir
    from os.path import abspath, exists
    
    home_dir = abspath('../../pyml/widgets')
    assert exists(home_dir)
    dirs_cache = set()
    
    for package in data:
        lk.logax(package)
        
        _dir = home_dir
        for d in package.split('.'):
            #   e.g. 'QtQuick.Controls' -> ['QtQuick', 'Controls']
            _dir += '/' + d
            if _dir not in dirs_cache:
                # this would be little faster than `os.path.exists(_dir)`
                dirs_cache.add(_dir)
                mkdir(d)

    del dirs_cache
    

def main():
    template: str = loads('../resources/template.txt')
    #   keywords: IMPORTS, WIDGET_NAME, PARENT_NAME, PROPS_TYPE_HINT,
    #       PROPS_INIT, ON_PROPS_CHAGNED, ON_SIGNALS_EMIT
    
    data_r: TypeHint.DataR = loads('../resources/no6_all_pyml_widgets.json')
    
    for package, v1 in data_r.items():
        for k2, v2 in v1.items():
            imports = ('from pyml._typing_hint import *',)
            widget_name = k2
            parent_name = v2['parent'] or 'Component'
            props_type_hint = _init_props(v2['props'], data_r)
            props_init = _init_props(v2['props'], data_r)
            
            dumps(template.format(
                IMPORTS=imports,
                WIDGET_NAME=widget_name,
                PARENT_NAME=parent_name,
                PROPS_TYPE_HINT='\n    '.join(
                    f'{p}: {t}' for (p, t) in props_type_hint
                ),
                PROPS_INIT='\n    '
            ), f'../../pyml/widgets/{package}')
            

def _init_props(props: dict[str, str], data: TypeHint.DataR):
    """
    在 `props` 参数中, 我们会遇到以下情况的属性类型:
        基础的类型: 例如 int, bool, string 等
        js 常见类型: 例如 Array, Object
            此外, Qt 也会用 list 代替 Array 表示 (在 Qt 文当值, 二者应该是混用
            的, 并不是很规范)
        qt 特有的类型: 例如 color, point, font, matrix4x4 等. 它们属于 'QML
            Basic Type'
        嵌套类型: 例如 Array<string>, list<Animation>
        同一包下的其他组件: 例如 AbstractBarSeries 的 axisX 属性的类型是
            'AbstractAxis', 这个 'AbstractAxis' 指的就是与 AbstractBarSeries 同
            属于一个包下的另一个组件
        不同包下的其他组件: 例如 TODO
        级联属性: 有两种格式:
            1. 以点号连接. 例如 `AbstractAxis3D.AxisOrientation`. 表示枚举值
                示例:
                    `AbstractAxis3D.AxisOrientation`:
                        Constant                                Value
                        ---------------------------------------------
                        QAbstract3DAxis::AxisOrientationNone    0x0
                        QAbstract3DAxis::AxisOrientationX       0x1
                        QAbstract3DAxis::AxisOrientationY       0x2
                        QAbstract3DAxis::AxisOrientationZ       0x4
                    `QAbstract3DSeries.Mesh`
                        Constant                                Value
                        ---------------------------------------------
                        QAbstract3DSeries::MeshUserDefined      0x0
                        QAbstract3DSeries::MeshBar              0x1
                        QAbstract3DSeries::MeshCube             0x2
                        QAbstract3DSeries::MeshPyramid          0x3
                        QAbstract3DSeries::MeshCone             0x4
                        QAbstract3DSeries::MeshCylinder         0x5
                        ...                                     ...
            2. 以双冒号连接. 例如 `QtQuick3D::Material`. 可能表示某个组件, 也可
                能表示枚举值.
                表示组件的情况:
                    例如 `QtQuick3D::Material` 表示 QtQuick3D 模块下的 Material
                    组件.
                表示枚举值的情况:
                    例如 `Qt::CursorShape`:
                        Constant            Value
                        -------------------------
                        Qt.ArrowCursor      ?
                        Qt.UpArrowCursor    ?
                        Qt.CrossCursor      ?
                        Qt.WaitCursor       ?
                        ...                 ...
        特殊的类型:
            keysequence, 来源于 `enum QKeySequence::StandardKey`, 我们需要预先写
                好这个 enumeration 类.
            QObject*: 来源于 `QtQuick.Item.containmentMask` 属性
            ...
    
    References:
        There're listed all types in `blueprint.template_generator.sidework
        .static_qml_basic_types()`
    """
    def recognize_plain_type(t: str):
        if t in ('array', 'list', 'Array'):
            return 'list'
        elif t in ('bool',):
            return 'bool'
        elif t in ('double', 'float', 'real'):
            return 'float'
        elif t in ('enum', 'enumeration', 'int'):
            return 'int'
        elif t in ('group',):
            # from pyml.properties.property_control import GPropertyControl
            return 'GPropertyControl'
        elif t in ('point',):
            return 'TPoint'
        elif t in ('string', 'url'):
            return 'str'
        elif t in ('stringlist', 'list<string>'):
            return 'list[str]'
        elif t in ('var', 'variant'):
            return '...'
    
    recog = recognize_plain_type
    known_widgets = set()
    for package, v1 in data.items():
        for widget in v1.keys():
            known_widgets.add(f'{package}.{widget}')
    
    for p, t in props.items():  # p: 'property'; t: 'type'
        if '<' in t and t.endswith('>'):
            #   e.g. 'list<string>'
            try:
                assert t.count('<') == 1
                a = t.split('<')[0]
                b = t.replace(a, '').strip('<>')
                yield p, f'{recog(a)}[{recog(b)}]'
            except AssertionError:
                assert t == 'list<list<point>>'
                yield p, f'list[list[TPoint]]'
        else:
            yield p, recog(t)
