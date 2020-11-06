"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : ast.py
@Version  : 0.3.2
@Created  : 2020-11-02
@Updated  : 2020-11-06
@Desc     :
    表述:
        - no, lineno: 行号. 格式为 'line{num}'.
        - ln, line: 行内容.
        - node: 节点, 组件节点. 见 Hint.AstNode
        - block: 组件声明域, 组件块. 同 node.
        - compdef: 组件声明域, 组件块. 同 node.
"""
import re

from pyml.core._typing_hints import AstHint as Hint


class SourceAst:
    """ Source code abstract syntax tree. """
    
    def __init__(self, source_code: str):
        """

        :param source_code: from `Mask.get_plain_text(merge_block=True)`
        """
        self.source_code = source_code
        self.source_tree = self._build_source_tree(self.source_code.split('\n'))
        self.source_map = self._build_source_map(self.source_tree)
        self.source_chain = self._build_source_chain(self.source_tree)

    @staticmethod
    def _build_source_tree(code_lines: list) -> Hint.SourceTree:
        virtual_root_node = {  # type: Hint.Node
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
        
        out = virtual_root_node['children']  # type: Hint.SourceTree
        return out
    
    @staticmethod
    def _build_source_map(tree: Hint.SourceTree):
        out = {}
        
        def _recurse(subtree: Hint.SourceTree):
            for lineno, node in subtree.items():
                out[lineno] = node
                _recurse(node['children'])
        
        _recurse(tree)
        return out
    
    @staticmethod
    def _build_source_chain(tree: Hint.SourceTree):
        from collections import defaultdict
        holder = defaultdict(list)
        
        def _recurse(subtree: Hint.SourceTree):
            for lineno, node in subtree.items():
                holder[node['level']].append(node)
                _recurse(node['children'])
        
        _recurse(tree)

        out = []
        for k in sorted(holder.keys()):
            out.append(holder[k])
        return out

    # --------------------------------------------------------------------------
    
    def get_compdef_blocks(self):
        """
        注意: 当前版本不支持嵌套组件声明. 也就是说:
            comp A:
                comp B:  # <- 不支持!
                    pass
        :return:
        """
        out = []
        for no, node in self.source_tree.items():
            assert node['level'] == 0
            if node['line_stripped'].startswith('comp '):
                out.append(node)
        return out
    
    @staticmethod
    def output_plain_text_from_struct(struct: Hint.Node):
        """ 将 struct 转换为纯字符串. 与 self._build_tree() 的过程相反. """
        out = [struct['line']]
        
        def _recurse(subtree: Hint.SourceTree):
            for no, node in subtree.items():
                out.append(node['line'])
                _recurse(node['children'])
        
        _recurse(struct['children'])
        return '\n'.join(out)


class ReferenceAst:  # DELETE: no usage
    
    def __init__(self, tree: Hint.SourceTree):
        self.tree = tree
        
    def scan(self):
        pass

    # noinspection PyMethodMayBeStatic
    def _scan_external_references(self):
        """ Scan `import...`, `from...` """
        return {}
    
    def _scan_object_references(self):
        out = {}
        
        def _recurse(subtree: Hint.SourceTree, holder: dict):
            for lineno, node in subtree.items():
                ln = node['line_stripped']
                if ln.startswith(('class ', 'def ', 'comp ')):
                    holder[lineno] = {k: v
                                      for (k, v) in node.items()
                                      if k != 'children'}
                    subholder = holder['children'] = {}
                    _recurse(node['children'], subholder)
        
        _recurse(self.tree, out)
        return out
    
    def _scan_component_references(self):
        pass
