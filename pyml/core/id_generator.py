from collections import defaultdict

from pyml._typing_hint import *


class IDGenerator:
    """
    ID 生成规则:
        1. 使用小写英文字母, 数字和下划线
        2. 以小写英文字母开头
        3. 为避免与组件内部属性冲突, 必须包含至少一个下划线
        4. 为避免与组件内部属性冲突, 以及保持一致性, 最好使用一个固定的开头
        5. 结合实际情况, 在理想的范围内提供理想的格式 (超出理想范围的极端情况,
           不强求格式美观)
        
    根据以上规则指导, 目前确定的生成格式如下:
        com_{block}_{no_a}_{no_b}_{no_c}_...
            1. 以 'com' 开头
            2. block 表示块 id, 用递增的 hex 值表示
               1. 之所以使用 hex, 是为了略微区分 no_a, no_b, no_c, ... 以便更好
                  地阅读
               2. 起始值是 '0x1'
            3. no_a, no_b, no_c, ... 各表示一个层级, 每个层级用独立增长的数字表
               示
               1. 每个层级的起始值是 '01'
               2. 当增长到 '99' 时, 下一个是 '100'
                  PS: 一般来说, 不可能增长这么大, 在 01 ~ 20 范围是最常见的
            2. 'com_{block}' 之后的每个下划线代表一个 '层级', 例如
               'com_0x1_01_01_01' 表示第一个 block 的第三层的第一个 item 的 uid
    """
    head = 'com'
    
    _block_index = 0x1
    _layer_level_2_com_no = defaultdict(TComponentNo)
    ''' {int TLayerLevel: int TComponentNo, ...}
        1. the keys are always in order
        2. layer_index starts from 0
        3. component_no starts from 1
    '''
    
    def new_block(self):
        self._block_index += 1
        return hex(self._block_index)
    
    @staticmethod
    def get_layer_level(uid: str) -> int:
        # e.g. 'com_0x1_01_02' -> ['com', '0x1', '01_02'] -> '01_02'
        # -> count one underline(s)
        return uid.split('_', 2)[-1].count('_')
    
    @staticmethod
    def get_parent_id(uid: TComponentID):
        out = uid.rsplit('_', 1)[0]
        if out.count('_') <= 1:
            return ''
        else:
            return out
    
    def main(self, layer_level: int):
        self._layer_level_2_com_no[layer_level] += 1
        
        if (a := layer_level) < (b := max(self._layer_level_2_com_no)):
            for i in range(a + 1, b + 1):
                self._layer_level_2_com_no.pop(i)
        
        return '{}_{}_{}'.format(
            self.head,
            hex(self._block_index),
            '_'.join(map(lambda x: '{:0>2}'.format(x),
                         self._layer_level_2_com_no.values()))
        )


# ------------------------------------------------------------------------------

id_gen = IDGenerator()
gen_id = id_gen.main
