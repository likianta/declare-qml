"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : ast.py
@Version  : 0.2.2
@Created  : 2020-11-02
@Updated  : 2020-11-04
@Desc     :
    表述:
        - no, lineno: 行号. 格式为 'line{num}'.
        - ln, line: 行内容.
        - node: 节点, 组件节点. 见 Hint.AstNode
        - block: 组件声明域, 组件块. 同 node.
        - compdef: 组件声明域, 组件块. 同 node.
"""
import re

from pyml.core._typing_hints import ComposerHint as Hint


class AST:
    
    def __init__(self, pyml_text: str):
        """

        :param pyml_text: from `Mask.get_plain_text(merge_block=True)`
        """
        self._text = pyml_text
        self._type_names = {  # No usage
            'import': 'import1',
            'from'  : 'import2',
            'def'   : 'def',
            'class' : 'class',
            'comp'  : 'comp_def',
        }
        self._tree = self._build_tree(self._text.split('\n'))
        self._flat_tree = self._build_flat_tree(self._tree)
    
    @staticmethod
    def _build_tree(code_lines: list) -> Hint.AstTree:
        virtual_root_node = {  # type: Hint.AstNode
            'lineno'  : '',
            'level'   : -4,  # abbreviation: lv
            'parent'  : None,
            'children': {}
            #           ^^ 这里才是我们最终要的结果, virtual_root_node 本身只是
            #              一个脚手架.
        }
        node_chain = [virtual_root_node]
        """ How does node chain work?

            if curr_lv > last_lv:
                [..., last_node] -> [..., last_node, curr_node]
                                                     ^ added
            if curr_lv == last_lv:
                [..., last_last_node, last_node] ->
                [..., last_last_node, curr_node]
                                      ^ substituted
            if curr_lv < last_lv:
                It depends on how many reverse indents:
                    -1 indent:
                        [..., lalalast_node, lalast_node, last_node] ->
                        [..., lalalast_node, curr_node]
                                             ^ substituted
                    -2 indents:
                        [..., lalalalast_node, lalalast_node,
                         lalast_node, last_node] ->
                        [..., lalalalast_node, curr_node]
                                               ^ substituted
                    -3 indents:
                        [..., lalalalalast_node, lalalalast_node,
                         lalalast_node, lalast_node, last_node] ->
                        [..., lalalalalast_node, curr_node]
                                                 ^ substituted
                    ...

            We can use pop-and-add action to implement it easily, please see it
            at "# === Node chain implementation ===".
        """
        
        last_lv = -4
        
        def _get_level(line):
            pattern = re.compile(r'^ *')
            whitespaces = pattern.match(line).group()
            return len(whitespaces)
            #   assert len(whitespaces) % 4 == 0
        
        for curr_no, curr_ln in enumerate(code_lines):
            #   curr_no: current line number; curr_ln: current line
            if curr_ln.strip() == '':
                continue
            
            curr_lv = _get_level(curr_ln)
            assert curr_lv % 4 == 0, (curr_no, curr_ln)
            
            # === Node chain implementation ===
            if curr_lv > last_lv:
                pass
            elif curr_lv == last_lv:
                node_chain = node_chain[:-1]
            else:
                pos = int(curr_lv / 4) + 1
                #   e.g. curr_lv = 0 -> pos = 1 -> data_node_chain = [root]
                node_chain = node_chain[:pos]
            curr_node = node_chain[-1]['children'].setdefault(
                f'line{curr_no}', {
                    'lineno'       : f'line{curr_no}',
                    #   'lineno'  : curr_no,
                    'line_stripped': curr_ln.strip(),
                    'line'         : curr_ln,
                    'level'        : curr_lv,
                    'parent'       : node_chain[-1]['lineno'],
                    #   'parent'  : node_chain[-1],  # 未采用, 这样会导致输出
                    #       json 时产生回环错误.
                    'children'     : {},
                }
            )
            node_chain.append(curr_node)
            
            last_lv = curr_lv
        
        out = virtual_root_node['children']  # type: Hint.AstTree
        return out
    
    @staticmethod
    def _build_flat_tree(tree):
        out = {}
        
        def _recurse(subtree: Hint.AstTree):
            for lineno, node in subtree.items():
                out[lineno] = node
                _recurse(node['children'])
        
        _recurse(tree)
        return out
    
    def get_compdef_blocks(self):
        """
        注意: 当前版本不支持嵌套组件声明. 也就是说:
            comp A:
                comp B:  # <- 不支持!
                    pass
        :return:
        """
        out = []
        for no, node in self._tree.items():
            assert node['level'] == 0
            if node['line_stripped'].startswith('comp '):
                out.append(node)
        return out
    
    @staticmethod
    def output_plain_text_from_struct(struct: Hint.AstNode):
        """ 将 struct 转换为纯字符串. 与 self._build_tree() 的过程相反. """
        out = [struct['line']]
        
        def _recurse(subtree: Hint.AstTree):
            for no, node in subtree.items():
                out.append(node['line'])
                _recurse(node['children'])
        
        _recurse(struct['children'])
        return '\n'.join(out)


class PymlAst(AST):  # DELETE ME or UPDATE
    
    def __init__(self, pyml_text: str):
        super().__init__(pyml_text)
        self._update_tree()

    def _update_tree(self):
        """
        在 Hint.AstNode 中增加以下信息:
            {
                ...
                'node_type': /str
                    'import',
                    'comp_def',
                    'comp_instance',
                    'prop_assign',
                    'on_signal',
                    'pseudo_field',
                    'class_def',
                    'func_def',
                /,
            }
        
        :return:
        """
        
        def _recurse(tree: Hint.AstTree):
            for node in tree.values():
                ln = node['line_stripped']
                if ln.startswith(('import ', 'from ')):
                    node['node_type'] = 'import'
                elif ln.startswith('comp '):
                    node['node_type'] = 'comp_def'
                elif ln.startswith('on_'):
                    node['node_type'] = 'on_signal'
                elif ln.startswith('<') and ln.endswith('>'):
                    node['node_type'] = 'pseudo_field'
                elif ln.startswith('class '):
                    node['node_type'] = 'class_def'
                elif ln.startswith('def '):
                    node['node_type'] = 'func_def'
                elif self._is_component_name(ln):
                    node['node_type'] = 'comp_instance'
                else:
                    node['node_type'] = 'prop_assigns'
                _recurse(node['children'])
                
        _recurse(self._tree)

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


'''
class CompAst(AST):  # DELETE ME
    
    def __init__(self, pyml_text: str):
        super().__init__(pyml_text)
        self._lock_to_compdef_blocks()
        self.ids = {}  # type: Hint.IDs
    
    def _lock_to_compdef_blocks(self):
        """ Filter top level nodes and get only 'comp_def' nodes. """
        
        def _get_keyword(line):
            # Take the first word as 'key'.
            pattern = re.compile(r'\w+')
            first_word = pattern.search(line).group()
            return first_word
        
        new_tree = {}  # type: Hint.AstTree
        for no, node in self._tree.items():
            assert node['level'] == 0
            if _get_keyword(node['line']) == 'comp':
                node['field'] = 'comp_def'
                new_tree[no] = node
        self._tree = new_tree
    
    def _add_field_info(self):
        
        def _get_keyword(line):
            # Take the first word as 'key'.
            pattern = re.compile(r'\w+')
            first_word = pattern.search(line).group()
            return first_word
        
        def _is_qml_comp_name(name):
            pattern = re.compile(r'[A-Z][a-zA-Z]+')
            if pattern.search(name):
                return True
            else:
                return False
        
        for node in self._tree.values():
            parent_node = self._flat_tree[node['parent']]
            if parent_node['field'] == 'comp_def':
                node['field'] = 'comp_block'
            keyword = _get_keyword(node['line'])
            if _is_qml_comp_name(keyword):
                node['field'] = 'comp_instance'
            else:
                pass
    
    def analyse_compdef_block(self):
        self._global_scanning()
        
        for block in self._tree.values():
            pass
    
    def _global_scanning(self):
        """ 扫描 id. """
        
        def _recurse(children: Hint.AstNode):
            for block in children:
                
                if block['type'] == 'comp_def':
                    pattern = re.compile(r'(?<=@)\w+')
                    if m := pattern.search(block['text']):
                        self.ids[m.group()] = block
                elif block['key'] == 'id':
                    pattern = re.compile(r'')
                    pass
                
                if 'children' in block:
                    _recurse(block['children'].values())
        
        _recurse(self._tree.values())
    
    def _line_scanning(self):
        pass
'''
