"""
@Author   : Likianta (likianta@foxmail.com)
@FileName : ast.py
@Version  : 0.1.0
@Created  : 2020-11-02
@Updated  : 2020-11-02
@Desc     : 
"""
import re

from pyml.core._typing_hints import ComposerHint as Hint


class AST:
    
    def __init__(self, pyml_text: str):
        """

        :param pyml_text: from `Mask.get_plain_text(merge_block=True)`
        """
        self._text = pyml_text
        self._type_names = {
            'import': 'import1',
            'from'  : 'import2',
            'def'   : 'def',
            'class' : 'class',
            'comp'  : 'comp_def',
        }
        self._tree = self._build_tree()
    
    def _build_tree(self) -> Hint.AstTree:
        root = tree = {  # type: Hint.AstTree
            'level'   : 0,  # abbreviation: lv
            'type'    : '',
            'children': {}
        }
        node_chain = [root]
        """ How does node chain work?

            if curr_lv > last_lv:
                [..., last_node] -> [..., last_node, curr_node]
                                                     ^ added
            if curr_lv == last_lv:
                [..., last_last_node, last_node] ->
                [..., last_last_node, curr_node]
                                      ^ substituted
            if curr_lv < last_lv:
                It depends on how many reverse indents:
                    -1 indent:
                        [..., lalalast_node, lalast_node, last_node] ->
                        [..., lalalast_node, curr_node]
                                             ^ substituted
                    -2 indents:
                        [..., lalalalast_node, lalalast_node,
                         lalast_node, last_node] ->
                        [..., lalalalast_node, curr_node]
                                               ^ substituted
                    -3 indents:
                        [..., lalalalalast_node, lalalalast_node,
                         lalalast_node, lalast_node, last_node] ->
                        [..., lalalalalast_node, curr_node]
                                                 ^ substituted
                    ...

            We can use pop-and-add action to implement it easily, please see it
            at "# === Node chain implementation ===".
        """
        
        # ----------------------------------------------------------------------
        
        def _get_level(line):
            pattern = re.compile(r'^ *')
            whitespaces = pattern.match(line).group()
            return len(whitespaces)
            #   assert len(whitespaces) % 4 == 0
        
        def _get_type(line):
            first_word = line.lstrip().split(' ', 1)[0]
            return {
                'import': 'import1',
                'from'  : 'import2',
                'def'   : 'def',
                'class' : 'class',
                'comp'  : 'comp_def',
            }.get(first_word, 'unsigned')
            #   the 2nd argument: unsigned expression, assignments, etc.
        
        # ----------------------------------------------------------------------
        
        last_lv = -4
        
        for ln_no, curr_ln in enumerate(self._text.split('\n')):
            #   ln_no: line number; curr_ln: current line
            if curr_ln.strip() == '':
                continue
            
            curr_lv = _get_level(curr_ln)
            assert curr_lv % 4 == 0, (ln_no, curr_ln)
            type_ = _get_type(curr_ln)
            
            # === Node chain implementation ===
            if curr_lv > last_lv:
                pass
            elif curr_lv == last_lv:
                node_chain = node_chain[:-1]
            else:
                pos = int(curr_lv / 4) + 1
                #   e.g. curr_lv = 0 -> pos = 1 -> data_node_chain = [root]
                node_chain = node_chain[:pos]
            curr_node = node_chain[-1]['children'].setdefault(
                f'line{ln_no}', {
                    'level'   : curr_lv,
                    'type'    : type_,
                    'children': {}
                }
            )
            node_chain.append(curr_node)
            
            last_lv = curr_lv
        
        from lk_utils.read_and_write import dumps
        dumps(tree, './test.json')  # TEST
        
        return tree


class CompAst(AST):
    
    def __init__(self, pyml_text: str):
        super().__init__(pyml_text)
        self._tree = self._lock_to_compdef_block()
    
    def _lock_to_compdef_block(self):
        """ Filter top level nodes and get only 'comp_def' nodes. """
        new_tree = {}
        for ln_no, node in self._tree.values():
            assert node['level'] == 0
            if node['type'] == 'comp_def':
                new_tree[ln_no] = node
        return new_tree
