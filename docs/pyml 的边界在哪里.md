举个例子:

1. pyml 对这种情况不报错:

```pyml
import pyml.qtquick.window

comp 123Window(Window): @win  # 1. QML 不允许数字开头的组件命名
    on_width: height ++  # 2. Python 不支持 `num++` 语法
```

2. pyml 对这种情况报错:

```pyml
comp Window  # 1. 'Window' 后面缺少冒号
    @win  # 2. '@' 语法必须在与 'comp' 同一行使用
```

这是因为, pyml 只对自己的语法规则做严格要求, 以保证能够依据 pyml 语法顺利生成 .qml 和 .py 文件. 至于生成的代码能否运行, 那是 QML 和 Python 的事情.

--------------------------------------------------------------------------------

PS: 对于示例 1, pyml 将生成以下代码:

```qml
// 123Window.qml
import QtQuick.Window 2.15

Window {
    id: win
    onWidthChanged: {
        PyML.call('method_230410', win)
    }
}

```

```python
from pyml.core import PyMLCore


class PyML(PyMLCore):
    
    def method_230410(self, win):
        prop0 = win.property('height')
        prop0 ++
        win.setProperty('height', prop0)

```
