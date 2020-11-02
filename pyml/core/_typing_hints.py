"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : _typing_hints.py
@Created : 2020-11-02
@Updated : 2020-11-02
@Version : 0.2.0
@Desc    :
"""
from typing import *


class RegexHint:
    import re
    RegexPattern = re.Pattern
    RegexMatch = re.Match


class AstHint:
    AstTreeNode = Dict[str, Any]
    """ -> {
            'level': <int 0, 4, 8, ...>,
            'type': <str 'import', 'from', 'def', 'class', 'comp', ...>,
            'children': {
                'line{num}': {
                    'level': ...,
                    ...
                },
                ...
            },
        }
    """
    AstTree = Dict[str, AstTreeNode]
    """ -> {str 'line{num}': dict ast_tree_node, ...} """


class ComposerHint(RegexHint, AstHint):
    PymlText = str
    MaskHolder = Dict[str, PymlText]
    """ -> {'mask_node_{num}': str source_pyml_text_snippet, ...} """


class CompAstHint(AstHint):
    """ Component Abstract Syntax Tree Type Hints. """
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
