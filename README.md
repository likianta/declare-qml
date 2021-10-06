> NOTE: English version is not complete yet, here is the Chinese version README.

> WIP: This project is in a very early stage. Any proposals and issues are welcomed!

# Declare-PySide | 声明式 PySide 界面库

`declare-pyside` 可以让开发者以 "声明式" 的纯 Python 语法编写可视化界面框架. 借助 Qt 强大的图形表达能力和 Python 简洁直观的嵌套式语法结构, 您将以全新的方式创造现代化的用户图形界面.

`declare-pyside` 在以下方面具有显著优势:

**1. 声明式的语法**

下面两张图分别展示了命令式语法 (左图) 和声明式语法 (右图) 的表现方式:

```py
from declare_pyside import *
from declare_pyside.widgets import *
from lk_lambdex import lambdex

""" Description

- Two lines of text are center in window.
- A button is under text lines.
- Click button to update text1's text and font size.
- The text2's text is synchronized to text1's text, but font size stayed.
"""

with Application() as app:

    with Window() as win:
        win.width = 600
        win.height = 400
        win.color = '#F2F2F2'
        win.visible = True
        
        with Text() as txt1:
            txt1.anchors.center_in = win
            txt1.font.pixel_size = 12
        
        with Text() as txt2:
            txt2.anchors.top = txt1.bottom
            txt2.text.bind(txt1.text)
            txt2.font.pixel_size.kiss(txt1.font.pixel_size)
            
        with Button() as btn:
            btn.anchors.top = txt2.bottom
            btn.text = 'Update Text'
            btn.clicked.connect(lambdex('', """
                txt1.text += '!'
                txt1.font.pixel_size += 1
            """))
```

[TODO]

**2. 健全的类型提示系统**

[TODO]

**3. 调用方式的优化**

[TODO]

**4. 热重载**

[TODO]

# 快速开始

`declare-pyside` 的组件基于 QML 组件生成. 如果您之前是 QML 开发者, 那么这个库的上手难度会小很多.

[TODO]
