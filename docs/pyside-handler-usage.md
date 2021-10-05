Related: `declare_qml.pyside.pyside.PySide.call.<docstring>`.

    class PySide(QObject, PyRegister):
        
        @Slot(TPyFuncName, result=TQVar)
        @Slot(TPyFuncName, TQVal, result=TQVar)
        @Slot(TPyFuncName, TQVal, TQVal, result=TQVar)
        def call(self, func_name: TPyFuncName, 
                 args: Optional[TQVal] = None,
                 kwargs: Optional[TQVal] = None):
            pass

# How We Use `PySide.call(...)` in QML Files

- `PySide.call(function)`
- `PySide.call(function, args)`
- `PySide.call(function, args, kwargs)`

**Typehint:**

`function`:

    JavaScript string. You need to make sure the function name has been registered in `declare_qml.pyside.pyside.PySide` before calling it.

`args`:

    JavaScript value, or array of values (something like Python `Union[object, list[object]]`).

`kwargs`: 

    JavaScript object (something like Python `dict`). Note that if `kwargs` is defined, the `args` must be array type.

# Quick Start

Have a look at the following example to get started it quickly:

Assume that our project tree is:

```
myproject/demo
|- main.py
|- test.qml
```

`main.py` source code:

```python
# main.py
from declare_qml import app, reg

@reg()  # register `hello_world` to qml.
def hello_world(*args, **kwargs):
    print(args, kwargs)
    
app.start('test.qml')
```

`test.qml` source code:

```qml
// test.qml
Item {
    Component.onCompleted: {
        // 1
        PySide.call('hello_world')
        // 2.1
        PySide.call('hello_world', 123)
        // 2.2
        PySide.call('hello_world', [123, 'abc'])
        // 3
        PySide.call('hello_world', [123, 'abc'], {a: 'aaa', 'b': 3})
    }
}
```

Screenshot of print in PyCharm console:

[TODO:AddScreenshots]

# Notice

## 01

```
Python Side:
    @reg()
    def aaa(x, *args): pass
QML Side:
    PySide.call('aaa', [1, 2, 3])
Result:
    x = 1, args = (2, 3)
```

## 02

```
Python Side:
    @reg()
    def aaa(x, *args): pass
QML Side:
    PySide.call('aaa', [[1, 2], 3])
Result:
    x = [1, 2], args = (3,)
```

## 03

```
Python Side:
    @reg()
    def aaa(x, *args): pass
QML Side:
    PySide.call('aaa', [[1, 2, 3]])
Result:
    x = [1, 2, 3], args = ()
```

## 04

```
Python Side:
    @reg()
    def aaa(x, *args): pass
QML Side:
    PySide.call('aaa', [[1, 2, 3]], {a: 'aaa', b: 1})
Result:
    [TODO:NeedTest]
```

## 05

```
Python Side:
    @reg()
    def aaa(x): pass
QML Side:
    PySide.call('aaa', [3])
Result:
    x = [3]
```
