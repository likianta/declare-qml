"""
@Author  : likianta <likianta@foxmail.com>
@Module  : _typing_hints.py
@Created : 2020-11-02
@Updated : 2020-11-04
@Version : 0.2.3
@Desc    :
"""
from typing import *


class RegexHint:
    import re
    RegexPattern = re.Pattern
    RegexMatch = re.Match


class AstHint:
    LineNo = str  # 之所以用 str, 是为了让 Python dict 在输出或读取 json 文件时
    #   键的类型一致 (用 int 作为键的话, json 文件中会转换成 str).
    """ -> 'line{num}' -> num: 从 0 开始数 """
    Node = Dict[str, Union[str, int, Dict[str, Any]]]
    """ -> {
            'lineno': str 'line{num}',
            'line': str,  # 原始的行内容. 便于还原输出
            'line_stripped': str,  # 去除了每行的前面的空格. 便于分析结构
            'level': <int 0, 4, 8, ...>,
            'parent': str lineno,
            'children': {
                lineno: Node,
                ...
            },
            ...
        }
    """
    NodeList = Union[List[Node], Iterable[Node]]
    SourceTree = Dict[LineNo, Node]
    """ -> {LineNo: Node, ...} """
    SourceMap = Dict[LineNo, Node]  # SourceTree 是嵌套的, SourceMap 是单层的.
    SourceChain = List[List[Node]]
    """ -> [[Node, ...], ...] """


class ComposerHint(RegexHint, AstHint):
    PymlText = str
    MaskHolder = Dict[str, PymlText]
    """ -> {'mask_node_{num}': str source_pyml_text_snippet, ...} """
    Component = Dict[str, Union[str, Dict[str, Any]]]
    """ -> {
            'field': <str 'comp_def', 'comp_instance', 'attr_def',
                      'prop_assign', 'py_expr'>,
            'general_props': {
                'id': <str 'root', 'win', 'rect', 'col', ...>,
                'objectName': str,
                'style': {
                    'width': <int, str>,
                    'height': <int, str>,
                    'size': <tuple, list, str>,
                    'pos': <tuple, list, str>,
                    ...
                },
                'parent': component_id,
                'children': [component_id, ...],
            },
            'specific_props': {
                # depends on which filed it is
            }
        }
    """
    IDs = Dict[str, Component]
    """ -> {
            buitin_id: comp, auto_id: comp, custom_id: comp
                -> buitin_id: 'root'
                -> auto_id: 'id1', 'id2', 'id3', ...
                -> custom_id: based on the source pyml code, notice that its
                    first letter must be a lower case (additional '_' before
                    first letter is allowed)
        }
    """
    PropAssigns = Dict[str, Dict[str, Tuple[str, str]]]
    """ -> {comp_id: {prop: (operator, expression), ...}, ...} """
