import os
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
        text = text.replace('{', '{{').replace('}', '}}')
        
        mask = Mask(text)
        
        # 字符串匹配
        mask.main(re.compile(r'([\'"]).*?(?<!\\)\1'))
        #

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
            origin text in the future.
        
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
        return self._text.format(**self._mask)


if __name__ == '__main__':
    mask = Mask(
        """'He didn\\'t tell you,' she says, "and me, too.\""""
    )
    mask.main(re.compile(r'([\'"]).*?(?<!\\)\1'))
    print(mask.masked_text)
    print(mask.plain_text)
    # See the result at '.assets/snipaste 2020-11-01 171109.png'
