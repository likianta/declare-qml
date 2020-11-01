"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : composer.py
@Created : 2020-11-01
@Updated : 2020-11-01
@Version : 0.1.1
@Desc    :
"""
import re
from contextlib import contextmanager


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
        with mask.temp_mask(re.compile(r'(?<!\\)"""'), '◆BLOCK_CMT◆', '"""'), \
             mask.temp_mask(re.compile(r"(?<!\\)'''"), "◇BLOCK_CMT◇", "'''"):
            mask.main(re.compile(r'([\'"]).*?(?<!\\)\1'))
        # 3. 块注释
        mask.main(re.compile(r'("""|\'\'\')(?:.|\n)*?(?<!\\)\1'))
        # 4. 行注释
        mask.main(re.compile(r'#.*'))
        # 5. 大中小括号
        mask.main(re.compile(r'\((?:.|\n)*?\)'))
        mask.main(re.compile(r'\[(?:.|\n)*?]'))
        mask.main(re.compile(r'{{(?:.|\n)*?}}'))
        
        # ----------------------------------------------------------------------
        # TEST
        from lk_utils import read_and_write
        from lk_utils.lk_logger import lk
        
        read_and_write.write_file(mask.plain_text, '../../tests/test2.txt')
        read_and_write.write_file(mask.masked_text, '../../tests/test.pyml')
        # noinspection PyProtectedMember
        read_and_write.write_json(mask._mask, '../../tests/test.json')
        lk.loga(mask.plain_text)
        lk.loga('\t-> ' + mask.masked_text)


class Mask:
    
    def __init__(self, text: str):
        self._index = 0
        self._text = text.replace('{', '{{').replace('}', '}}')
        self._mask = {}  # {str mask_holder: str raw_text}
    
    def replace(self, fo, to, cnt=-1):  # DELETE ME
        self._text = self._text.replace(fo, to, cnt)
    
    @contextmanager
    def temp_mask(self, fo: re.Pattern, to: str, restore=''):
        try:
            self._text = fo.sub(to, self._text)
            yield self
        finally:
            self._text = self._text.replace(to, restore or fo.pattern)
    
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
            key = self._create_mask_holder(match_str)
            self._text = self._text.replace(match_str, f'{{{key}}}', 1)
            # # noinspection PyTypeChecker
            # self._safely_replace(*match.span(0), key)
    
    def _safely_replace(self, start: int, end: int, mask_holder: str):
        """ 安全地替换目标片段为 mask_holder.
        
        NOTE: This method has no usage for now.
        
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
        key, val = f'mask_node_{self._index}', s
        self._mask[key] = val
        return key
    
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
        pattern = re.compile(r'(?:{{)*{mask_node_\d+}(?:}})*')
        #   注意: 这里的 'mask_node_\d+' 与 `self._create_mask_holder()` 中的键
        #   格式有关.
        text = self._text
        while pattern.search(text):
            try:
                text = text.format(**self._mask)
            except Exception as e:
                read_and_write.write_file(
                    text, './pyml_composer_error.txt'
                )
                read_and_write.write_file(
                    self._mask, './pyml_composer_error.json'
                )
                raise e
        return text.replace('{{', '{').replace('}}', '}')


if __name__ == '__main__':
    from lk_utils import read_and_write
    
    composer = Composer(read_and_write.read_file('../../tests/test1.txt'))
    # noinspection PyProtectedMember
    composer._collapse_code_block()
