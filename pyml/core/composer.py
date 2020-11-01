"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : composer.py
@Created : 2020-11-01
@Updated : 2020-11-02
@Version : 0.1.5
@Desc    :
"""
import re
from contextlib import contextmanager

from lk_logger import lk


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


class Mask:
    
    def __init__(self, text: str):
        self._index = 0
        self._holder_pattern = re.compile(r'{mask_holder_\d+}')
        self._conflicts = self._holder_pattern.findall(text)
        self._text = self._holder_pattern.sub('{mask_holder_conflict}', text)
        self._mask = {}  # {str mask_holder: str raw_text}
        
        if self._conflicts:
            lk.loga('find conflicts', len(self._conflicts))
    
    @contextmanager
    def temp_mask(self, pattern: re.Pattern, restore=''):
        """
        NOTE: 您需要保证 pattern 的形式足够简单, 它应该只匹配到 "一个" 特定的字
            符串, 例如:
                # wrong
                pattern = re.compile(r'\d\d')
                pattern = re.compile(r'\w+')
                ...
                
                # right (仅使用准确的描述, 可以加上前瞻, 后顾的条件)
                pattern = re.compile(r'11')
                pattern = re.compile(r'(?<=0x)001A')
                pattern = re.compile(r'32(?!\w)')
                ...
            restore 一般来说和 pattern 要匹配的目标字符串是一致的. 比如
            `pattern = re.compile(r'11')` 对应的 restore 就是 '11',
            `pattern = re.compile(r'(?<=0x)001A')` 对应的 restore 是 '001A'.
        
        :param pattern:
        :param restore:
        :return:
        """
        restore = restore or pattern.pattern
        try:
            holder = self._create_mask_holder(restore)
            self._text = pattern.sub(holder, self._text)
            yield self
        finally:
            # noinspection PyUnboundLocalVariable
            restore_pattern = re.compile(r'(?<!{)' + holder + r'(?!})')
            self._text = restore_pattern.sub(restore, self._text)
    
    def main(self, pattern: re.Pattern):
        """
        E.g.
            self._text = '\'He didn\\\'t tell you,\' she says, "and me, too."'
                          |        ^--^            |           ^------------^
                          ^------------------------^
            -> self._mask = {
                'mask1': '\'He didn\\\'t tell you,\'',
                          |        ^--^            |
                          ^------------------------^
                'mask2': '"and me, too."',
                          ^------------^
            }
            -> self._text = '{mask1} she says, {mask2}'
            
            So we can use `self._text.format(**self._mask)` to restore the
            origin text in the future (see `self.plain_text()`).
        
        :param pattern:
        :return:
        """
        text = self._text
        for match in pattern.finditer(text):
            match_str = match.group(0)
            holder = self._create_mask_holder(match_str)
            self._text = self._text.replace(match_str, holder, 1)
            #   # noinspection PyTypeChecker
            #   self._safely_replace(*match.span(0), holder)
    
    def _safely_replace(self, start: int, end: int, mask_holder: str):
        """ 安全地替换目标片段为 mask_holder.
        
        FIXME: 此方法未被调用过, 且未通过用例测试 (需要检视和修复).
        
        E.g.
            from: 'a = "x, y"'
                  |    ^----^|
                  ^----------^
            to: 'a = {mask1}'
                |    ^-----^|
                ^-----------^
            #   self._mask = {'mask1': '"x, y"'}
        E.g.
            from: 'a = "\'\'\'x, \'y\\\'\'\'\'"'
                  |    ||        ^-----^     |||
                  |    |^1-2-3-----------4-5-6||
                  |    ^----------------------^|
                  ^----------------------------^
            to: 'a = "{mask1}"'
                |    |^-----^||
                |    ^-------^|
                ^-------------^
            #   self._mask = {'mask1': '\'\'\'x, \'y\\\'\'\'\''}
                                       ||        ^-----^     ||
                                       |^--------------------^|
                                       ^----------------------^
        """
        self._text = '{0}{{{1}}}{2}'.format(
            self._text[:start], mask_holder, self._text[end:]
        )
    
    def _create_mask_holder(self, s: str):
        self._index += 1
        key, val = f'mask_holder_{self._index}', s
        self._mask[key] = val
        return '{' + key + '}'
    
    @property
    def masked_text(self):
        return self._text
    
    @property
    def plain_text(self):
        """
        E.g.
            # origin_text = 'a = "x and y" \\ \n    "and z"'
            self._text = 'a = {mask2}'
            self._mask = {
                'mask1': '\\ \n',
                'mask2': '"x and y" {mask1}    "and z"',
            }
            ->
                result = 'a = "x and y" \\ \n    "and z"'
                # assert result == origin_text
        """
        pattern = self._holder_pattern
        text = self._text
        _error_stack = []
        
        while pattern.search(text):
            _error_stack.append('---------------- ERROR STACK ----------------')
            _error_stack.append(text)
            
            try:
                for holder in set(pattern.findall(text)):
                    text = text.replace(
                        holder, self._mask[holder[1:-1]]
                        #                 ^ '{mask_holder_1}' -> 'mask_holder_1'
                    )
            except Exception as e:
                from lk_utils import read_and_write
                read_and_write.dumps(
                    _error_stack, f1 := './pyml_composer_error.txt'
                )
                read_and_write.dumps(
                    self._mask, f2 := './pyml_composer_error.json'
                )
                raise Exception(
                    e, f'Plese check dumped info from [{f1}] and [{f2}] for '
                       f'more infomation.'
                )
            
        else:
            if text == self._text:
                lk.loga('No mask node found')
        
        for holder in self._conflicts:
            text = text.replace('{mask_holder_conflict}', holder, 1)
        
        del _error_stack
        return text


if __name__ == '__main__':
    from lk_utils import read_and_write
    
    composer = Composer(read_and_write.read_file('../../tests/test1.txt'))
    # noinspection PyProtectedMember
    composer._collapse_code_block()
