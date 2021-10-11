from declare_pyside import app
from declare_pyside.widgets import *


@app.build
def build(root=None):
    with Text() as txt:
        txt.text = 'Centered Text'
        txt.anchors.center_in = root


if __name__ == '__main__':
    build()
