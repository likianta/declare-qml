"""
DELETE: this module is going to be removed.
"""
class Inspect:
    
    def __init__(self):
        self._source_dict = {}  # type: dict[str, tuple[str, ...]]
        self._source = None
    
    def chfile(self, file):
        # from lk_logger import lk
        # lk.loga(file)
        if file not in self._source_dict:
            with open(file, 'r', encoding='utf-8') as f:
                self._source_dict[file] = tuple(
                    line.rstrip() for line in f
                )
        self._source = self._source_dict[file]
    
    def get_line(self, lineno) -> str:
        return self._source[lineno - 1]


inspect = Inspect()
