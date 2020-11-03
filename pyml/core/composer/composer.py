"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : composer.py
@Version  : 0.2.9
@Created  : 2020-11-02
@Updated  : 2020-11-04
@Desc     :
"""
import re

from lk_logger import lk

from pyml.core._typing_hints import ComposerHint as Hint
from pyml.core.composer.ast import AST
from pyml.core.composer.mask import Mask


class Composer:
    
    def __init__(self, pyml_text: str):
        self._pyml_text = pyml_text
        #   self._pyml_text = re.sub(r'\t', '    ', pyml_text)
    
    def main(self):
        mask = self._collapse_code_block()
        ast = AST(mask.plain_text)
        comp_blocks = ast.get_compdef_blocks()
        for block in comp_blocks:
            ComponentComposer(ast.output_plain_text_from_struct(block), block)
            # TODO
    
    def _collapse_code_block(self):
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
                 
        这样, 得到的处理后的代码是严格按照缩进来表示嵌套层次的代码, 有利于后面用
        `pyml.core.composer.ast.AST` 构建语法树.

        :ref: 'docs/Composer 掩码处理效果示例.md'
        :return:
        """
        mask = Mask(self._pyml_text)
        
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
        
        return mask


class ComponentComposer:
    
    def __init__(self, pyml_text, comp_block: Hint.AstNode):
        self._pyml_text = pyml_text
        self._comp_block = comp_block  # a single comp block
        self._comp_block_tree = {comp_block['lineno']: comp_block}
        
        self.ids = {}  # type: Hint.IDs
        self._build_ids()  # `self._comp_block` and `self.ids` got updated
        self._build_field()

    def _build_ids(self):
        """
        
        :return: {
                ...
                'context': {
                    relative_id: absolute_id,
                        -> relative_id: <'root', 'parent', 'self'>
                        -> absolute_id: see `self.ids` dict
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
    
        def _recurse(tree: Hint.AstTree, parent):
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

    def _build_field(self):
        """
        
        :return: {
                'field': <'comp_def', 'comp_body', 'attr', 'style', 'children'>,
                ...
            }
        """
        pattern = re.compile(r'<(\w+)>')
        
        def _recurse(subtree: Hint.AstTree):
            for node in subtree.values():
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
    
    _simple_num = 0  # see `self._register_id`
    
    def _register_id(self, node: Hint.AstNode, comp_id=''):
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

    def main(self):
        prop_assigns = self._extract_property_assignments()
        self._refine_property_assignments(prop_assigns)

    def _extract_property_assignments(self):
        out = {}  # {parent_id: {property: (operator, raw_expression)}}
        
        pattern = re.compile(
            r'(_*[a-z]\w*) *(<=|=>|<=>|:=|::|:|=) *(.*)'
            # ^----------^  ^-------------------^  ^--^
            #  property      operator               expression
        )
        
        pseudo_fields = (
            'children', 'attr', 'style',
        )
        
        def _recurse(tree: Hint.AstTree):
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
    
                        def _recurse_expr_block(tree: Hint.AstTree):
                            nonlocal expr
                            for node in tree.values():
                                expr += node['line'] + '\n'
                                _recurse_expr_block(node['children'])
    
                        _recurse_expr_block(node['children'])
                    
                    x = out.setdefault(node['context']['self'], {})
                    x[prop] = (oper, expr)
        
        _recurse(self._comp_block['children'])
        return out

    def _refine_property_assignments(self, prop_assigns: Hint.PropAssigns):
        py_side = []
        qml_side = []

        
