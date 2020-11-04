"""
@Author   : likianta (likianta@foxmail.com)
@FileName : composer.py
@Version  : 0.1.0
@Created  : 2020-11-04
@Updated  : 2020-11-04
@Desc     : 将 pyml 代码编译为 .py & .qml 代码.
    
    注: 请根据 'docs/PyML 实现流程.mm' 进行.

"""
from pyml.core.composer.ast import PymlAst


def compile_pyml_code(pyml_code: str):
    """
    
    :param pyml_code: read from .pyml file.
    :return:
    """
    ast = PymlAst(pyml_code)
