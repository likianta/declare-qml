from pyml._typing_hint import *
from pyml.keywords import const
from .property_control import GPropertyControl


# noinspection PyUnusedLocal
class Anchors(GPropertyControl):
    fill: TConstable[TComponentID]
    center: TConstable[TComponentID]
    
    left: TConstable[TComponentID]
    right: TConstable[TComponentID]
    top: TConstable[TComponentID]
    bottom: TConstable[TComponentID]
    
    margins: Union[int, tuple[int, ...], list[int]]
    left_margin: TConstable[int]
    right_margin: TConstable[int]
    top_margin: TConstable[int]
    bottom_margin: TConstable[int]
    
    def _init_properties(self):
        self.fill = ''
        self.center = ''
        self.left = ''
        self.right = ''
        self.top = ''
        self.bottom = ''
        self.margins = 0
        self.left_margin = 0
        self.right_margin = 0
        self.top_margin = 0
        self.bottom_margin = 0
    
    def on_fill_changed(self, v):
        self.left = self.right = self.top = self.bottom = const(v)
        self.center = ''
    
    def on_left_changed(self, v):
        if self.fill != v: self.fill = const('')
        if v: self.center = const('')
    
    def on_right_changed(self, v):
        if self.fill != v: self.fill = const('')
        if v: self.center = const('')
    
    def on_top_changed(self, v):
        if self.fill != v: self.fill = const('')
        if v: self.center = const('')
    
    def on_bottom_changed(self, v):
        if self.fill != v: self.fill = const('')
        if v: self.center = const('')
    
    def on_center_changed(self, v):
        self.fill = self.left = self.right = self.top = self.bottom = const('')
    
    def on_hcenter_changed(self, v):
        if v: self.left = self.right = const('')
    
    def on_vcenter_changed(self, v):
        if v: self.top = self.bottom = const('')
    
    def on_margins_changed(self, v):
        self.left_margin = self.right_margin = \
            self.top_margin = self.bottom_margin = const(v)
    
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


class DialectAnchors(Anchors):
    lcenter: TComponentID
    rcenter: TComponentID
    tcenter: TComponentID
    bcenter: TComponentID
    hcenter: TComponentID
    vcenter: TComponentID
    
    lside: TComponentID
    rside: TComponentID
    tside: TComponentID
    bside: TComponentID
    hside: TComponentID
    vside: TComponentID
    
    lmargin: int
    rmargin: int
    tmargin: int
    bmargin: int
    hmargins: int
    vmargins: int
