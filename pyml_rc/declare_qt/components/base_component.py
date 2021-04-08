from declare_foundation.components import BaseComponent as _Base


class BaseComponent(_Base):
    
    def _add_self_to_parent(self, child_com, parent_com):
        if parent_com is not None:
            child_com.setParent(parent_com)
