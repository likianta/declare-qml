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
            mask.main(
                re.compile(r'([\'"]).*?(?<!\\)\1'), cmd='strip_linebreaks'
            )
        # 3. 块注释
        mask.main(re.compile(r'("""|\'\'\')(?:.|\n)*?(?<!\\)\1'), cmd='abandon')
        # 4. 行注释
        mask.main(re.compile(r'#.*'), cmd='abandon')
        # 5. 大中小括号
        mask.main(re.compile(r'\((?:.|\n)*?\)'), cmd='strip_linebreaks')
        mask.main(re.compile(r'\[(?:.|\n)*?]'), cmd='strip_linebreaks')
        mask.main(re.compile(r'{{(?:.|\n)*?}}'), cmd='strip_linebreaks')
        
        return mask


class ComponentComposer:
    
    def __init__(self, block: CompAstHint.AstNode):
        self._block = block
        self.ids = {
            'root': block,
        }  # type: CompAstHint.IDs
    
    def global_scanning(self):
        """ Find and store ids. """
        
        # noinspection PyUnboundLocalVariable
        def _recurse(children: CompAstHint.AstNode):
            for child_node in children:
                ln = child_node['line']
                if ('@' in ln) and \
                        (match := re.compile(r'(?<= @)\w+').search(ln)):
                    key = match.group().split('@', 1)[1]
                    self.ids[key] = child_node
                elif (ln.startswith('id')) and \
                        (match := re.compile(r'^id *: *\w+').search(ln)):
                    key = match.group().rsplit(':', 1)[-1].strip()
                    self.ids[key] = child_node
                _recurse(child_node['children'].values())
                
        _recurse([self._block])

    def line_scanning(self):
        pass
