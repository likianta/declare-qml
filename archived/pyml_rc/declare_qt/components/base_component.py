from PySide6.QtWidgets import QLayoutItem

from declare_foundation.components import BaseComponent as _Base


class BaseComponent(_Base):
    
    def _enter_extra(self):
        if isinstance(self, QLayoutItem):
            # 注意: 当 self 是 QLayoutItem 实例时, 必须在 __enter__ 时期立即让父
            # 组件添加它 (父组件调用 setLayout 方法). 否则, Application 在启动时
            # 会出现一个空白的小窗口 (这个小窗口就是未指定父组件时的 self), 小窗
            # 口直到父组件添加它后会以闪退的方式消失, 给用户造成 "有什么窗口一闪
            # 而过" 的感觉.
            from ..core import parent
            parent_com = parent.represents
            assert parent_com is not None
            parent_com.setLayout(self)
    
    def _exit_extra(self, child_com, parent_com):
        # PS: self is child_com, they are the same object
        if isinstance(self, QLayoutItem):
            return
        if parent_com is not None:
            if isinstance(parent_com, QLayoutItem):
                parent_com.addWidget(child_com)
            else:
                child_com.setParent(parent_com)
        if hasattr(self, 'show'):
            self.show()
