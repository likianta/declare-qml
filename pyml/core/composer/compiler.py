"""
@Author   : likianta (likianta@foxmail.com)
@FileName : composer.py
@Version  : 0.1.0
@Created  : 2020-11-04
@Updated  : 2020-11-04
@Desc     : 将 pyml 代码编译为 .py & .qml 代码.
    
    注: 请根据 'docs/PyML 实现流程.mm' 进行.

"""
from pyml.core.composer.ast import SourceAst
from pyml.core.composer.composer import ComponentComposer, PlainComposer
from pyml.core._typing_hints import ComposerHint as Hint
from lk_utils.read_and_write import read_file


def main(pyml_file: str):
    compile_pyml_code(read_file(pyml_file))


def compile_pyml_code(pyml_code: str):
    """
    
    :param pyml_code: read from .pyml file.
    :return:
    """
    # create ast
    ast = SourceAst(pyml_code)
    
    # compose
    lines_holder = {}
    
    lines_holder.update(
        _compose_plain_code(ast.source_tree).lines
    )
    _compose_component_block(ast.source_tree)


def _compose_plain_code(tree: Hint.SourceTree):
    composer = PlainComposer()
    
    def _recurse(subtree: Hint.SourceTree):
        for no, node in subtree.items():
            composer.submit(node)
            _recurse(subtree['children'])
    
    _recurse(tree)
    return composer


def _compose_component_block(tree: Hint.SourceTree):
    for no, node in tree.items():
        assert node['level'] == 0
        if node['line_stripped'].startswith('comp '):
            block = node
        else:
            continue
            
        composer = ComponentComposer(block)
