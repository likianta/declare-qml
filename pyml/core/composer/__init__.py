"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : __init__.py
@Version  : 0.2.0
@Created  : 2020-11-02
@Updated  : 2020-11-02
@Desc     :
"""
import re

from pyml.core._typing_hints import CompAstHint
from pyml.core.composer.ast import AST
from pyml.core.composer.mask import Mask


class Composer:
    
    def __init__(self, pyml_text: str):
        self.pyml_text = pyml_text
        #   self.pyml_text = re.sub(r'\t', '    ', pyml_text)
    
    def main(self):
        mask = self._collapse_code_block()
        ast = AST(mask.plain_text)
        comp_blocks = ast.get_compdef_blocks()
        for block in comp_blocks:
            pass
    
    def _collapse_code_block(self):
        """ 折叠 "代码块". 将块注释, 行注释, 字符串, 括号等替换为掩码, 以便于后
            续的代码分析.

        :ref: 'docs/Composer 掩码处理效果示例.md'
        :return:
        """
        mask = Mask(self.pyml_text)
        
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
        mask.main(re.compile(r'\((?:.|\n)*?\)'), cmd='strip_linebreaks')
        mask.main(re.compile(r'\[(?:.|\n)*?]'), cmd='strip_linebreaks')
        mask.main(re.compile(r'{{(?:.|\n)*?}}'), cmd='strip_linebreaks')
        
        return mask


class ComponentComposer:
    
    def __init__(self, comp_block: CompAstHint.AstNode):
        self._comp_block = comp_block
        self.ids = {
            'root': comp_block,
        }  # type: CompAstHint.IDs
        
    def main(self):
        self._extend_props()
        self.global_scanning()
        self.line_scanning()

    def _extend_props(self):
    
        def _recurse(nodes: CompAstHint.AstNodeList):
            for node in nodes:
                node.update({
                    'attr' : {},
                    'style': {},
                })
                _recurse(node['children'].values())
    
        _recurse((self._comp_block,))

    def global_scanning(self):
        """ Find and store ids. """
        
        # noinspection PyUnboundLocalVariable
        def _recurse(nodes: CompAstHint.AstNodeList):
            for node in nodes:
                ln = node['line']
                if ('@' in ln) and \
                        (match := re.compile(r'(?<= @)\w+').search(ln)):
                    key = match.group().split('@', 1)[1]
                    self.ids[key] = node
                elif (ln.startswith('id')) and \
                        (match := re.compile(r'^id *: *\w+').search(ln)):
                    key = match.group().rsplit(':', 1)[-1].strip()
                    self.ids[key] = node
                _recurse(node['children'].values())
                
        _recurse((self._comp_block,))
        
    # def _update_prop(self, node, prop, value):
    #     if prop not in node:
    #         node[prop] = []
    #     node[prop].append(value)

    def line_scanning(self):
        operator_pattern = re.compile(r'<=|=>|<=>|:=|::|:|=')
        
        def _get_comp_name(line):
            p1 = re.compile(r'comp (\w+)\((\w+)\):')
            p2 = re.compile(r'comp (\w+):')
            
            if m := p1.search(line):
                return m.group(2), m.group(1)
            elif m := p2.search(line):
                return m.group(1), m.group(1)
        
        comp_name_qml, comp_name_py = _get_comp_name(self._comp_block['line'])
        qml_codes = [f'{comp_name_qml}:']
        py_codes = [f'class {comp_name_py}(PymlObject):']
        
        buitin_props = {}
        custom_props = {}  # {str prop: [comp1, comp2, comp3, ...], ...}
        
        def _recurse(parent, line_nodes: CompAstHint.AstNodeList):
            for node in line_nodes:
                ln = node['line']
                if ln.startswith('attr '):
                    """ e.g.
                    attr path: str
                    attr path: 'abc'
                    attr path: {'dir': ..., 'name': ...}
                    attr path: FileBrowse
                    attr path: FileBrowse:
                        attr dir: ...
                        attr name: ...
                    attr path: FileBrowse()
                    ...
                    """
                    op = operator_pattern.search(ln).group()
                    prop, expr = map(lambda x: x.strip(), ln.split(op, 1))
                    prop = prop.replace('attr ', '', 1)
                    x = custom_props.setdefault(prop, [])
                    x.append()
                    
                    qml_codes.append(
                        ' ' * node['level'] + 'property var {prop}'
                    )
                    py_codes.append(
                    
                    )
                    