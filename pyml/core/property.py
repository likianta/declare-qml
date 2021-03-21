# noinspection PyProtectedMember
from sys import _getframe

from pyml._typing_hint import *
from pyml.keywords.keywords import Final


class _Property:
    __initialized = False
    __propagating = False
    __propagations: set
    
    def __init__(self):
        self._init_properties()
        self.__propagations = set()
        self.__initialized = True
    
    def _init_properties(self):
        raise NotImplementedError
    
    # def __getattr__(self, item):
    #     if (
    #             isinstance(item, str) and
    #             item.startswith('on_') and
    #             item.endswith('_changed')
    #     ):
    #         return self.__dict__.get(item, lambda v: v)
    #     else:
    #         return self.__dict__[item]
    
    def __setattr__(self, key, value, propagate=True):
        
        if self.__initialized:
            # noinspection PyTypeHints
            if isinstance(value, Final):
                value = value.value
                send_signal = False
            else:
                send_signal = True
                
                ''' 如何避免无限回调?
                1. self._propagations 维护一个传播链
                2. 当 on_prop_changed 的 prop 第一次触发时, 由于该 prop 不在传播
                    链上, 所以正常触发
                    1. 此时 self._propagations 记录该 prop
                3. 当 prop 因为某种联动机制再次到来时, 由于不是第一次触发,
                    self._propagations 有记录, 所以不予触发, 直接返回
                4. 什么时候清空传播链? 当外部调用者触发时 (由下面的语句判断是否
                    为外部调用者), 将传播链清零, 并重复步骤 2 的过程
                '''
                # https://www.cnblogs.com/hester/articles/4767152.html
                caller_name = _getframe(1).f_code.co_name  # type: str
                if (
                        caller_name.startswith('on_') and
                        caller_name.endswith('_changed')
                ):  # the caller is from inner method, so we prevent it if not
                    # the first time triggered follows step 3
                    if key in self.__propagations:
                        return
                    # else it it the first time occurred, we pass through it
                    # follows step 2
                else:
                    # else the caller is from outside, so we clear the
                    # propagation chain and pass through it follows step 2
                    self.__propagations.clear()
                self.__propagations.add(key)
        else:
            send_signal = False
        
        super().__setattr__(key, value)
        
        if send_signal:
            getattr(self, f'on_{key}_changed', lambda v: v)(value)


class QProperty(_Property):
    """ QQuickItem Property (原生属性) """
    
    def _init_properties(self):
        raise NotImplementedError


class GProperty(_Property):
    """ GroupProperty (属性组|级联属性) """
    
    def _init_properties(self):
        raise NotImplementedError


class LProperty(_Property):
    """ Linkage Property (联动属性) """
    
    def _init_properties(self):
        raise NotImplementedError


# ------------------------------------------------------------------------------

# noinspection PyUnusedLocal
class Anchors(GProperty):
    fill = ''  # type: TComponentID
    center = ''  # type: TComponentID
    hcenter = ''  # type: TComponentID
    vcenter = ''  # type: TComponentID
    
    left = ''  # type: TComponentID
    right = ''  # type: TComponentID
    top = ''  # type: TComponentID
    bottom = ''  # type: TComponentID
    
    margins = 0  # type: Union[int, tuple[int, ...], list[int]]
    left_margin = 0  # type: int
    right_margin = 0  # type: int
    top_margin = 0  # type: int
    bottom_margin = 0  # type: int
    
    def _init_properties(self):
        pass
    
    # def __getattr__(self, item):
    #     if item in ('on_left_changed', 'on_right_changed',
    #                 'on_top_changed', 'on_bottom_changed'):
    #         return lambda v: self._on_side_changed(item, v)
    #     else:
    #         return self.__dict__[item]
    
    def on_fill_changed(self, v):
        self.left = self.right = self.top = self.bottom = v
        self.center = ''
    
    # # def _on_side_changed(self, side, v):
    # #     if self.fill != v: self.fill = ''
    # #     if v: self.center = ''
    
    def on_left_changed(self, v):
        if self.fill != v: self.fill = ''
        if v: self.center = ''
    
    def on_right_changed(self, v):
        if self.fill != v: self.fill = ''
        if v: self.center = ''
    
    def on_top_changed(self, v):
        if self.fill != v: self.fill = ''
        if v: self.center = ''
    
    def on_bottom_changed(self, v):
        if self.fill != v: self.fill = ''
        if v: self.center = ''
    
    def on_center_changed(self, v):
        self.fill = self.left = self.right = self.top = self.bottom = ''
    
    def on_hcenter_changed(self, v):
        if v: self.left = self.right = ''
    
    def on_vcenter_changed(self, v):
        if v: self.top = self.bottom = ''
    
    def on_margins_changed(self, v):
        self.left_margin = self.right_margin = \
            self.top_margin = self.bottom_margin = v
    
    def __str__(self):
        out = []
        
        if self.fill:
            if self.left == self.right == self.top == self.bottom == self.fill:
                out.append(f'anchors.fill: {self.fill}')
        elif self.center:
            out.append(f'anchors.centerIn: {self.center}')
        else:
            if self.hcenter:
                out.append(f'anchors.horizontalCenter: {self.hcenter}')
            else:
                if self.left:
                    out.append(f'anchors.left: {self.left}')
                if self.right:
                    out.append(f'anchors.right: {self.right}')
            if self.vcenter:
                out.append(f'anchors.verticalCenter: {self.vcenter}')
            else:
                if self.top:
                    out.append(f'anchors.left: {self.top}')
                if self.bottom:
                    out.append(f'anchors.left: {self.bottom}')
        
        if self.margins:
            out.append(f'anchors.margins: {self.margins}')
        if self.left_margin != self.margins:
            out.append(f'anchors.leftMargin: {self.left_margin}')
        if self.right_margin != self.margins:
            out.append(f'anchors.rightMargin: {self.right_margin}')
        if self.top_margin != self.margins:
            out.append(f'anchors.topMargin: {self.top_margin}')
        if self.bottom_margin != self.margins:
            out.append(f'anchors.bottomMargin: {self.bottom_margin}')
        
        return '\n'.join(out)
