"""
@Author   : likianta <likianta@foxmail.com>
@FileName : pyml_interp.py
@Version  : 0.2.1
@Created  : 2020-11-06
@Updated  : 2020-11-08
@Desc     : PyML Interpreter based on PyML AST.
"""
import re
from collections import defaultdict

from lk_logger import lk

from pyml.core.composer.ast import SourceAst
from pyml.core._typing_hints import InterpreterHint as Hint


# noinspection PyMethodMayBeStatic
class PymlInterpreter:
    """
    PyML 解释器基于抽象语法树进行解读, 阐述每个树节点的功能含义.
    PyML 解释器仅负责解释和描述功能, 如何实现这些功能, 将由 PythonComposer 和
    QmlComposer 决定.
    
    QA:
        Q: 如何理解 PyML 只解释节点功能?
        A: 假设有一段源代码 `comp A: @alpha`, PyML 解读为:
                {
                    'node_type': 'comp_def',
                    'comp_name': 'A',
                    'comp_parent_name': 'Item',
                    'comp_id': 'alpha',
                }
            对于所有节点, PyML 都会给出类似于这样的信息, 以字典格式呈现.
            这些信息仅仅是字典, 并不能够真实的功能和样式. 所以之后我们需要:
            1. PythonComposer 把后端的功能以 Python 代码的形式生成:
                class A(PymlCore):
                    def __init__(self):
                        super().__init__()
                        self.id = 'alpha'
                        self.comp_name = 'A'
                        self.comp_parent_name = 'Item'
                    ...
            2. QMLComposer 把前端的功能以 QML 代码的形式生成:
                // A.qml
                Item {
                    id: alpha
                    ...
                }
        Q: 为什么基于抽象语法树解读?
        A: 抽象语法树的 source_tree, source_map, source_chain 数据在分析过程中很
            有帮助; 直接分析源码 (str) 的话反而不方便.
            您可以类比理解为 json 文件和 Python dict 的关系, 直接解析 json (str)
            的话不方便, 将它转换为 dict 后对程序来说更易做进一步处理.
    """
    
    def __init__(self, ast: SourceAst):
        self.source_tree = ast.source_tree
        self.source_map = ast.source_map
        self.source_chain = ast.source_chain
        
        self.data = defaultdict(dict)
        
        self._context = ['top_module']  # type: Hint.Context
        # self._node = None  # type: Hint.Node
    
    def _global_scanning(self):
        pass
    
    def mainloop(self):
        ref_resolver = ReferenceResolver()
        
        for lineno, node in self.source_tree.items():
            # self._node = node
            
            node_type, value = self._check_node_type(node, top_module_only=True)
            
            # 判断顺序 (按编者习惯): 由易到难
            if node_type == 'raw_pycode':
                self.submit(node)
            elif node_type == 'import':
                ref_resolver.analyse_import(value)
            elif node_type == 'comp_def':
                comp = ComponentInterpreter(node, ref_resolver)
                comp.main()
                pass
            
    def submit(self, node: Hint.Node, include_subnodes=True):
        self.data[node['lineno']] = node['line']
        
        def _recurse(subtree: Hint.SourceTree):
            for lineno, node in subtree.items():
                self.data[lineno] = node['line']
                _recurse(node['children'])
        
        if include_subnodes:
            _recurse(node['children'])
        
    def _check_node_type(self, node: Hint.Node,
                         top_module_only=False) -> Hint.NodeType:
        """
        
        :return: <str 'raw_pycode'>
        """
        if top_module_only is False:
            raise Exception('暂不支持对任意层级的节点做节点类型分析, 请将'
                            '`top_module_only` 参数设为 True.')

        ln = node['line_stripped']

        def _get_pyml_module():
            return ln.split(' ')[1]
            #   'import pyml.qtquick' -> 'pyml.qtquick'

        def _get_comp_name():
            pattern = re.compile(r'comp +(\w+)\((\w+)\):|comp +(\w+):')
            """ 1. 'comp MyWindow(Window):' -> ('MyWindow', 'Window')
                2. 'comp Window:' -> ('Window',)
            """
            a, b, c = pattern.search(ln)
            """ 'comp MyWindow(Window):' -> a, b, c = 'MyWindow', 'Window', None
                'comp Window:'           -> a, b, c = None, None, 'Window'
            """
            return a or c
            
        def _get_raw_line():
            return node['line']
            
        if ln.startswith(('import ', 'from ')):
            return 'import', _get_pyml_module()
        elif ln.startswith('comp '):
            return 'comp_def', _get_comp_name()
        else:
            return 'raw_pycode', _get_raw_line()
    
    # --------------------------------------------------------------------------
    
    def main2(self, node):  # DEL
        """

        :param node:
        :return: {
                'type': str,
                key: value,
                ...
                    -> key: based on which 'type' is
                    -> value: <str, list, dict>
            }
        """
        # self.node = node
        if node['node_type'] == 'comp_def':
            return self._dissolve_comp_def(node)
        elif node['node_type'] == 'pseudo_field':
            return {}
        elif node['node_type'] == 'comp_instance':
            return self._dissolve_comp_instance(node)
        elif node['node_type'] == 'on_signal':
            return self._dissolve_on_signal(node)
        elif node['node_type'] == 'prop_assigns':
            pass
    
    def _dissolve_prop_assigns(self, node):
        pattern = re.compile(
            r'(_*[a-z][.\w]*) *(<==>|<=>|==|<=|=>|:=|::|:|=) *(.*)'
            # ^-------------^  ^---------------------------^  ^--^
            #  property         operator                       expression
            #                   注意: operator 的匹配符号的顺序必须是从长到短排
        )
        match = pattern.search(node['line_stripped'])
        prop, oper, expr = \
            match.group(1), match.group(2), match.group(3)
        
        # analyse expression
        
        return {
            'type'      : 'prop_assign',
            'property'  : prop,
            'operator'  : oper,
            'expression': '',
            'ids'       : {
            
            }
        }
    
    def _dissolve_on_signal(self, node):
        pattern = re.compile(r'on_([^_]+)')
        signal = pattern.search(node['line_stripped']).group(1)
        return {
            'type'         : 'on_signal',
            'signal'       : signal,
            'passive_voice': signal.endswith('ed')
        }
    
    def _dissolve_comp_instance(self, node):
        pattern = re.compile(r'\w+')
        name = pattern.match(node['line_stripped']).group()
        return {
            'type'     : 'comp_instance',
            'comp_name': name
        }
    
    def _dissolve_comp_def(self, node):
        """
        E.g.
            IN: comp Window: @win
            OT: {
                    'type': 'comp_def',
                    'parent_comp_name': 'Window',
                    'self_comp_name': 'Window',
                    'id': 'win', ...
                }
        """
        pattern = re.compile(r'comp +(\w+)\((\w+)\):|comp +(\w+):')
        a, b, c = pattern.search(node['line_stripped'])
        """
            'comp MyWindow(Window):' -> a, b, c = 'MyWindow', 'Window', None
            'comp Window:'           -> a, b, c = None, None, 'Window'
        """
        return {
            'type'            : 'comp_def',
            'parent_comp_name': a or c,
            'self_comp_name'  : b or c,
        }


class ReferenceResolver:
    
    def __init__(self):
        from lk_utils.read_and_write import loads
        self.all_modules = loads('../../data/pyml_import_namespaces.json')
        self.imports = []
        self.available_components = set()
    
    def analyse_import(self, module: str):
        """
        
        :param module: e.g. 'pyml.qtquick.controls'
        :return:
        """
        if module.startswith('pyml'):
            self.imports.insert(0, module)
            self.available_components.update(
                self.all_modules[module].keys()
            )
    
    def get_comp_props(self, comp_name: str):
        """
        
        :param comp_name: e.g. <'Rectangle', 'Text', 'Window', ...>
        :return:
        """
        out = []
        
        def _recurse(module, comp_name):
            node = self.all_modules[module][comp_name]  # type: dict
            out.extend(node['props'])
            if node['inherits']:
                _recurse(module, node['inherits'])
        
        for m in self.imports:
            if comp_name in self.all_modules[m]:
                _recurse(m, comp_name)
                break
        else:
            raise Exception
        
        return out
        

class ComponentInterpreter:
    """ 一个 ComponentInterpreter 实例负责解析一个 Component Code Block. """
    
    def __init__(self, comp_block: Hint.Node, ref_resolver: ReferenceResolver):
        self.lines = defaultdict(list)  # {source_lineno: lines, ...}
        self._ref_resolver = ref_resolver

        self._comp_block = comp_block  # a single comp block
        self._comp_block_tree = {comp_block['lineno']: comp_block}

        self.ids = {}  # type: Hint.IDs
        self._build_ids()  # `self._comp_block` and `self.ids` got updated
        self._build_fields()
        self._build_node_types()
    
    def _build_ids(self):
        """

        :return: {
                ...
                'context': {
                    relative_id: absolute_id,
                        -> relative_id: <'root', 'parent', 'self'>
                        -> absolute_id: see `self.ids` dict
                    custom_id: absolute_id,
                    ...
                }
            }
        """
        
        # noinspection PyUnboundLocalVariable
        def _custom_id(line: str):
            # please pass node['line_stripped'] to the param
            if ('@' in line) and \
                    (match := re.compile(r'(?<= @)\w+').search(line)):
                _id = match.group(0)
            elif (line.startswith('id')) and \
                    (match := re.compile(r'^id *: *(\w+)').search(line)):
                _id = match.group(1)
            else:
                _id = ''
            return _id
        
        def _recurse(tree: Hint.SourceTree, parent):
            for node in tree.values():
                if self._is_component_name(node['line_stripped']):
                    node['context'] = {
                        'root'  : 'root',
                        'parent': parent['context']['self'],
                        'self'  : self._register_id(node),
                    }
                else:
                    node['context'] = parent['context']
                    
                    # 位置写得有点分散, 待优化
                    if _id := _custom_id(node['line_stripped']):
                        self._register_id(parent, _id)
                
                _recurse(node['children'], node)
        
        # ----------------------------------------------------------------------
        
        self._comp_block.update({
            'context': {
                'root'  : 'root',
                'parent': '',
                'self'  : self._register_id(self._comp_block, 'root'),
            }
        })
        # 位置写得有点分散, 待优化
        if _id := _custom_id(self._comp_block['line_stripped']):
            self._register_id(self._comp_block, _id)
        
        _recurse(self._comp_block['children'], self._comp_block)
    
    def _build_fields(self):
        """

        :return: {
                'field': <'comp_def', 'comp_body', 'attr', 'style', 'children'>,
                ...
            }
        """
        pattern = re.compile(r'<(\w+)>')
        
        def _recurse(tree: Hint.SourceTree):
            for node in tree.values():
                ln = node['line_stripped']
                if ln.startswith('comp '):
                    field = 'comp_def'
                elif m := pattern.match(ln):
                    field = m.group(1)
                else:
                    field = 'comp_body'
                node['field'] = field
                _recurse(node['children'])
        
        _recurse(self._comp_block_tree)
    
    def _build_node_types(self):
        """

        :return: {
                'node_type': <
                    str
                        'class_def',
                        'comp_def',
                        'comp_instance',
                        'func_def',
                        'import',
                        'on_signal',
                        'prop_assign',
                        'pseudo_field',
                >,
                ...
            }
        """
        _temp_token = ''
        
        def _recurse(tree: Hint.SourceTree):
            nonlocal _temp_token
            
            for node in tree.values():
                ln = node['line_stripped']
                # simple
                if ln.startswith(('import ', 'from ')):
                    node['node_type'] = 'import'
                elif ln.startswith('comp '):
                    node['node_type'] = 'comp_def'
                elif ln.startswith('class '):
                    node['node_type'] = 'class_def'
                elif ln.startswith('def '):
                    node['node_type'] = 'func_def'
                # not stable
                elif ln.startswith('<') and ln.endswith('>'):
                    node['node_type'] = 'pseudo_field'
                elif ln.startswith('on_'):
                    node['node_type'] = 'on_signal'
                # complex
                elif ln.endswith('::'):
                    node['node_type'] = 'prop_assigns'
                    _temp_token = '::'
                elif self._is_component_name(ln) and _temp_token == '':
                    node['node_type'] = 'comp_instance'
                else:
                    node['node_type'] = 'prop_assigns'
                
                _recurse(node['children'])
                _temp_token = ''
        
        _recurse(self._comp_block_tree)
    
    # --------------------------------------------------------------------------
    
    _simple_num = 0  # see `self._register_id`
    
    def _register_id(self, node: Hint.Node, comp_id=''):
        if comp_id == '':
            self._simple_num += 1
            comp_id = f'id{self._simple_num}'
        # self.ids[comp_id] = node  # A
        self.ids[comp_id] = node['lineno']  # B
        # setattr(self.ids, comp_id, node)
        return comp_id
    
    @staticmethod
    def _is_component_name(name) -> bool:
        """ 这是一个临时的方案, 用于判断 name 是否为组件命名格式: 如果是, 则认为
            它是组件; 否则不是组件.

        WARNING: 该方法仅通过命名格式来判断, 不具有可靠性! 未来会通过分析 import
            命名空间来判断.

        :param name: 请传入 node['line_stripped'] <- node: CompAstHint.AstNode
        :return:
        """
        pattern = re.compile(r'[A-Z]\w+')
        return bool(pattern.match(name))
    
    # --------------------------------------------------------------------------
    
    def main(self):
        # 逐节点解释
        pass
    
    def _check_node_type(self, node: Hint.Node) -> Hint.CompProp:
        pass
    
    def _extract_property_assignments(self):
        out = {}  # {parent_id: {property: (operator, raw_expression)}}
        
        pattern = re.compile(
            r'(_*[a-z]\w*) *(<==>|<=>|==|<=|=>|:=|::|:|=) *(.*)'
            # ^----------^  ^---------------------------^  ^--^
            #  property      operator                       expression
            #                注意: operator 的匹配符号的顺序必须是从长到短排
        )
        
        pseudo_fields = (
            'children', 'attr', 'style',
        )
        
        def _recurse(tree: Hint.SourceTree):
            for node in tree.values():
                
                if node['field'] in pseudo_fields:
                    _recurse(node['children'])
                    continue
                
                for match in pattern.finditer(node['line_stripped']):
                    prop, oper, expr = \
                        match.group(1), match.group(2), match.group(3)
                    lk.loga('{:15}\t{:^5}\t{:<}'.format(prop, oper, expr))
                    #        ^A--^  ^B--^  ^C-^
                    #   A: 右对齐, 宽度 15; B: 居中, 宽度 5; C: 左对齐, 宽度不限
                    
                    if expr:
                        """
                        说明遇到了这类情况 (示例):
                            width: height + 10
                        根据 pyml 语法要求, 单行的属性赋值, 不可以有子语法块, 也
                        就是说下面的情况是不允许的:
                            width: height + 10
                                if height + 10 > 10:
                                    return 10
                                else:
                                    return height
                        """
                        assert bool(node['children']) is False
                    else:
                        """
                        说明遇到了这类情况 (示例):
                            width:
                                if height > 10:
                                    return 10
                                else:
                                    return height
                        其中 prop = 'width', oper = ':', expr 捕获到的是 '', 但
                        其实应该取它的块结构. 所以下面我们就做这个工作.
                        """
                        
                        def _recurse_expr_block(tree: Hint.SourceTree):
                            nonlocal expr
                            for node in tree.values():
                                expr += node['line'] + '\n'
                                _recurse_expr_block(node['children'])
                        
                        _recurse_expr_block(node['children'])
                    
                    x = out.setdefault(node['context']['self'], {})
                    x[prop] = (oper, expr)
        
        _recurse(self._comp_block['children'])
        return out
