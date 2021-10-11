from declare_pyside import *
from declare_pyside.widgets import *
from lk_lambdex import lambdex

""" Description

- Two lines of text are center in window.
- A button is under text lines.
- Click button to update text1's text and font size.
- The text2's text is synchronized to text1's text, but font size stayed.
"""

# with Application() as app:
#     with Window() as win:
#         win.width = 600
#         win.height = 400
#         win.color = '#F2F2F2'
#         win.visible = True


@app.build
def build(win):
    win.width = 600
    win.height = 400
    win.color = '#F2F2F2'
    win.visible = True
    
    with Text() as txt1:
        txt1.text = 'Hello (1)'
        # txt1.anchors.center_in = win
        txt1.x = 50
        txt1.y = 30
        txt1.font.pixel_size = 12
    
    with Text() as txt2:
        txt2.text = 'Hello (2)'
        txt2.anchors.top = txt1.anchors.bottom
        # txt2.text.bind(txt1.text)
        txt1.qobj.textChanged.connect(lambdex('text', """
            txt2.text = txt1.text
        """))
        txt2.font.pixel_size = txt1.font.pixel_size
    
    with Button() as btn:
        btn.anchors.top = txt2.anchors.bottom
        btn.text = 'Update'
        btn.qobj.clicked.connect(lambdex('', """
            txt1.text += '!'
            txt1.font.pixel_size += 1
        """))


if __name__ == '__main__':
    build()
