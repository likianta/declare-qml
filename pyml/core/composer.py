import re


class Composer:
    pyml_text: str
    
    def __init__(self, pyml_text: str):
        self.pyml_text = pyml_text
    
    def _mask(self):
        """
        IO:
            before
                the pyml text is:
                    def aaa(
                        x, y
                    ):
                        z = '{}' + '''
                    {0}:{1}
                    '''.format(x, y)
            # after
                text changed to:
                    def aaa({mask0}):
                        z = '{{}}' + '''{mask1}'''.format(x, y)
                with background _mask info:
                    mask_info = {
                        'mask0': '\n    x, y\n',
                        'mask1': '\n{{0}}:{{1}}\n',
                    }
        :return:
        """
        text = self.pyml_text
        
        mask = Mask(text)
        # 1. 将末尾以 \\ 换行的内容拼接回来.
        #    例如 'a = "xy" \\\n    "z"' -> 'a = "xy" {mask}    "z"'.
        #    经过这样处理后, 我们可以保证代码的所有缩进 (除下面要处理的掩码外)
        #    都是严格表达层级关系的.
        mask.main(re.compile(r'\\ *\n'))
        # 2. 字符串掩码
        #    示意图: '.assets/snipaste 2020-11-01 171109.png'
        mask.main(re.compile(r'([\'"]).*?(?<!\\)\1'))
        # 3. 行注释与块注释
        mask.main(re.compile(r'#.*$'))
        #   mask.main(re.compile(r'#(?:.|\s)*$'))
        mask.main(re.compile(r'("""|\'\'\')(?:.|\s)*?\1'))
        # 4. 大中小括号


class Mask:
    
    def __init__(self, text: str):
        self._index = 0
        self._text = text
        self._mask = {}  # {str mask_holder: str raw_text}
    
    def main(self, pattern: re.Pattern):
        """
        E.g.
            self._text = '\'He didn\\\'t tell you,\' she says, "and me, too."'
            #             |        ^--^            |           ^------------^
            #             ^------------------------^
            -> self._mask = {
                'mask1': '\'He didn\\\'t tell you,\'',
                #         |        ^--^            |
                #         ^------------------------^
                'mask2': '"and me, too."',
                #         ^------------^
            }
            -> self._text = '{mask1} she says, {mask2}'
            
            So we can use `self._text.format(**self._mask)` to restore the
            origin text in the future (see `self.plain_text()`).
        
        :param pattern:
        :return:
        """
        text = self._text
        for match in pattern.finditer(text):
            match = match.group(0)
            key = self._create_mask_holder(match)
            self._text = self._text.replace(
                match, f'{{{key}}}', 1
            )
    
    def _create_mask_holder(self, s: str):
        self._index += 1
        key, val = f'mask{self._index}', s
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
        pattern = re.compile(r'{mask\d+}')
        text = self._text
        while pattern.search(text):
            text = text.format(**self._mask)
        return text
