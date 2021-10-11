from lk_lambdex import lambdex
from lk_logger import lk

from declare_pyside import *
from declare_pyside.widgets import *


@app.build
def build(root=None):
    lk.loga(root)
    
    with Text() as txt:
        txt.text = 'Hello World'
    
    with Button() as btn:
        btn.x = 100
        btn.y = 60
        btn.text = 'CLICK ME'
        btn.qobj.clicked.connect(lambdex('', """
            txt.text += '!'
        """))
        lk.loga(btn.qobj)
    
    with Rectangle() as rect0:
        rect0.object_name = '#rect0'
        rect0.width = 80
        rect0.height = 40
        rect0.color = '#1A0DB5'  # deepblue
        rect0.x = btn.x
        rect0.y = btn.y + btn.height + 3
        # rect0.anchors.left = btn.anchors.left
        # rect0.anchors.top = btn.anchors.bottom
        
        with Rectangle() as rect1:
            rect1.object_name = '#rect1'
            rect1.width = 30
            rect1.height = 40
            rect1.color = '#9F2281'  # purple
            rect1.anchors.center_in = rect0
            
            with MouseArea() as area:
                area.object_name = '#area'
                area.anchors.fill = rect1
                area.drag.target = rect0
                
        with Text() as txt:
            txt.text = 'Drag the purple zone to move deepblue rectangle.'
            txt.anchors.top = rect0.anchors.bottom


if __name__ == '__main__':
    build()
