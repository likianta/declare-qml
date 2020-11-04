"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : lang_interp.py
@Created : 2020-11-04
@Updated : 2020-11-04
@Version : 0.1.0
@Desc    : Language oriented interpreter.
    
    本模块用于将 pyml 语法转换为其他声明式 ui 的语法. 目前主要提供面向 qml 的转
    换. 例如:
    
    # pyml           | // qml
    on_completed ::  | Component.onCompleted {
        pass         |     // pass
                     | }
"""
import re


class BaseConverter:
    code: list
    info: dict
    
    def __init__(self):
        self.code = []
        self.info = {}
        
    def submit(self):
        self.code.append(
            ''
        )


class PythonConverter(BaseConverter):
    pass


class QmlConverter(BaseConverter):
    prop: str
    oper: str
    expr: str
    
    def main(self, prop: str, oper: str, expr: str, **kwargs):
        self.prop, self.oper, self.expr = prop, oper, expr
        
        if prop.startswith('on_'):
            self._convert_onprop(
                kwargs['pymethod'],
                kwargs.get('args', [])
            )
            
    def _convert_onprop(self, pymethod, args):
        s = self.prop.split('_')
        p = s[0] + ''.join(map(lambda x: x.title(), s[1:]))
        if not p.endswith('ed'):
            p += 'Changed'
        p += ': '
        self.prop = p
        
        assert self.oper == '::'
        self.oper = '''{{ return PyML.call("{0}", {1}) }}'''.format(
            pymethod, {
                0: '',
                1: args[0],
            }.get(len(args), '[' + ','.join(args) + ']')
        )
