from uuid import uuid1

from .generic import Property
from ...typehint import *


class PyFunc(Property):
    is_static = False

    # noinspection PyMissingConstructor
    def __init__(self, coms: Iterable[TComponent], func: Callable):
        # coms: 'components'; _relcoms: 'related components'
        self._relcoms = [str(x.uid) for x in coms]
        self._func_id = _gen_id()
        self.value = func
    
    def adapt(self) -> str:
        return 'PySide.call("{}", [{}])'.format(
            self._func_id,
            ', '.join(self._relcoms)
        )
        # return f'PySide.call("{self._func_id}", {self._relcoms})'


def _gen_id():
    # e.g. 'func_af0322bed55011eb89cbbeecaf0f60d0'
    return f'func_{str(uuid1()).replace("-", "")}'
