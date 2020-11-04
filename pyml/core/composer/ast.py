"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : ast.py
@Version  : 0.3.0
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


class PymlAst:
    
    def __init__(self, pyml_code: str):
        """

        :param pyml_code: from `Mask.get_plain_text(merge_block=True)`
        """
        self.source_code = self._collapse_code_block(pyml_code)
        self.source_tree = self._build_source_tree(self.source_code.split('\n'))
        self.source_map = self._build_source_map(self.source_tree)
        self.source_chain = self._build_source_chain(self.source_tree)

    @staticmethod
    def _collapse_code_block(source_code: str) -> str:
        """ 折叠 "代码块". 将块注释, 行注释, 字符串, 括号等替换为掩码, 以便于后
            续的代码分析.
            
        本方法的目的是, 将原 pyml 代码中的所有可消除的换行符消除. 例如:
            indent | code
                 0 | def calc(
                 4 |     x, y
                 0 | ):
                 4 |     a = (
                 8 |         x + y
                 4 |     ) * 2
        变为:
            indent | code
                 0 | def calc(x, y):
                 4 |     a = (x + y) * 2
                 
        这样, 得到的处理后的代码是严格按照缩进来表示嵌套层次的代码, 有利于后面根
        据缩进量来快速构建代码树.

        :ref: 'docs/掩码处理效果示例.md'
        :return:
        """
        from pyml.core.composer.mask import Mask
        mask = Mask(source_code)
    
        # 1. 将末尾以 \\ 换行的内容拼接回来.
        #    例如 'a = "xy" \\\n    "z"' -> 'a = "xy" {mask}    "z"'.
        mask.main(re.compile(r'\\ *\n'), cmd='strip_linebreaks')
        # 2. 字符串掩码
        #    示意图: '.assets/snipaste 2020-11-01 171109.png'
        with mask.temp_mask(re.compile(r'(?<!\\)"""'), '"""'), \
             mask.temp_mask(re.compile(r"(?<!\\)'''"), "'''"):
            mask.main(re.compile(r'([\'"]).*?(?<!\\)\1'),
                      cmd='strip_linebreaks')
        # 3. 块注释
        mask.main(re.compile(r'^ *("""|\'\'\')(?:.|\n)*?(?<!\\)\1'),
                  cmd='abandon')
        #    非块注释, 长字符串
        mask.main(re.compile(r'("""|\'\'\')(?:.|\n)*?(?<!\\)\1'),
                  cmd='strip_linebreaks')
        # 4. 行注释
        mask.main(re.compile(r'#.*'), cmd='abandon')
        # 5. 大中小括号
        mask.main(re.compile(r'\((?:[^(]|\n)*?\)'),
                  cmd='circle+strip_linebreaks')
        mask.main(re.compile(r'\[(?:[^\[]|\n)*?]'),
                  cmd='circle+strip_linebreaks')
        mask.main(re.compile(r'{(?!mask_holder_\d+})(?:[^{]|\n)*?}'),
                  cmd='circle+strip_linebreaks')
        #    到这一步, 会出现 `{A, {mask1}, {mask2}, B}` 的情况, 我们需要把最外
        #                      ^----------------------^
        #    边的花括号也折叠.
        mask.main(re.compile(
            r'{(?!mask_holder_\d+})(?:{mask_holder_\d+}|[^}])*?}'
            # ||  ^A-------------^||  ^B--------------^ ^C-^|  |
            # |^D-----------------^^E-----------------------^  |
            # ^F-----------------------------------------------^
            #   A: 当左花括号右边不是 `mask_holder_\d+}` 时继续
            #   B: 当匹配到 `{mask_holder_\d+}` 时继续
            #   C: 或者当匹配到非 `}` 时继续 (包括: 遇到换行符, 也继续)
            #   F: 非贪婪地匹配, 直到遇到了不符合 B, C 情形的右花括号结束
        ), cmd='strip_linebreaks')
    
        return mask.plain_text

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
