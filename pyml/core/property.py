from pyml._typing_hint import *

from .mechanism import AutoDerivedProperty


class GenericProperty:
    pass


# noinspection PyUnusedLocal
class Anchors(AutoDerivedProperty):
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
    
    # def __getattr__(self, item):
    #     if item in ('on_left_changed', 'on_right_changed',
    #                 'on_top_changed', 'on_bottom_changed'):
    #         return lambda v: self._on_side_changed(item, v)
    #     else:
    #         return self.__dict__[item]
    
    # def __setattr__(self, key, value, propagate=True):
    #     super().__setattr__(key, value, propagate)
    
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
