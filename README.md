# PYML 是什么?

PYML 是 Python 版的 QML, 可在声明式 UI 中引用 Python 的模块.

PYML 受 enaml 启发而诞生, 与 enaml 有诸多相似之处.

PYML 写出来的代码看起来长这样:

```pyml
"""
效果图见 "gallery/pyml-intro.gif".
"""
from pyml.widgets.api import *


comp MyWindow(Window): @_win  
    #   1. `comp` 是关键字, 表示声明一个组件, 类似于 `class`
    #   2. `@_win` 是一种简写, 相当于 `id: _win`
    
    style:  # 该组件的所有样式都在 style 中定义
        background_color: '#cccccc'
        padding: 10
        size: (600, 800)  # 等同于 `width: 600` & `height: 800`
        
    Rectangle: @_rect
        style:
            width: 100
            height: 100
            anim:
                NumberAnimation:
                    style:
                        width: _win.inner_width
                        height: _win.inner_height
                    duration: 1000  # |int ms, str |'1s', '1m', '1h', ...||
                    interpolator: Easing.OutQuart


if __name__ == '__main__':
    from pyml.core import Application
    with Application() as app:
        win = MyWindow()
        win.show()
        app.start()

``` 
