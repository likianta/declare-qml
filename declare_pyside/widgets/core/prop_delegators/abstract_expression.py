from .typehint import *


# DELETE: this module is going to be removed.
class AbstractDelegatorExpression:
    qobj: TQObject
    expression: str
    
    def __init__(self, qobj):
        self.qobj = qobj
        self.expression = ''
    
    # def _randomize_placeholders(self, expression: str):
    #     def _gen_random_slot_name():
    #         return 'x' + token_hex(8)
    
    def update(self, value: str):
        self.expression += value
        return self.expression
