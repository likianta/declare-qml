"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : __init__.py
@Version  : 0.1.0
@Created  : 2020-11-02
@Updated  : 2020-11-02
@Desc     :
"""
import re

from pyml.core.composer.mask import Mask


class Composer:
    
    def __init__(self, pyml_text: str):
        self.pyml_text = pyml_text
        #   self.pyml_text = re.sub(r'\t', '    ', pyml_text)
    
    def _collapse_code_block(self):
        """ 折叠 "代码块". 将块注释, 行注释, 字符串, 括号等替换为掩码, 以便于后
            续的代码分析.

        :ref: 'docs/Composer 掩码处理效果示例.md'
        :return:
        """
        mask = Mask(self.pyml_text)
        
        # 1. 将末尾以 \\ 换行的内容拼接回来.
        #    例如 'a = "xy" \\\n    "z"' -> 'a = "xy" {mask}    "z"'.
        mask.main(re.compile(r'\\ *\n'))
        # 2. 字符串掩码
        #    示意图: '.assets/snipaste 2020-11-01 171109.png'
        with mask.temp_mask(re.compile(r'(?<!\\)"""'), '"""'), \
             mask.temp_mask(re.compile(r"(?<!\\)'''"), "'''"):
            mask.main(re.compile(r'([\'"]).*?(?<!\\)\1'))
        # 3. 块注释
        mask.main(re.compile(r'("""|\'\'\')(?:.|\n)*?(?<!\\)\1'))
        # 4. 行注释
        mask.main(re.compile(r'#.*'))
        # 5. 大中小括号
        mask.main(re.compile(r'\((?:.|\n)*?\)'))
        mask.main(re.compile(r'\[(?:.|\n)*?]'))
        mask.main(re.compile(r'{{(?:.|\n)*?}}'))
        
        return mask
