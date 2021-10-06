# declare-pyside 的动态绑定机制是如何实现的

首先, 我们设置一个问题场景:

```python
from declare_pyside.widgets import Window, Item


with Window():

    with Item() as A:
        A.x = 0
        
    with Item() as B:
        B.x = 0
        
    with Item() as C:
        C.x = 0
    
    # 现在我们想让 A.x 与其他对象的 x 属性动态绑定. 当其他对象的 x 改变时, A.x 
    # 也得到更新.
    # 下面展示几种可能出现的情形 (稀有度从低到高).
    
    A.x.bind(B.x)  # 1
    A.x.bind(B.x + 1)  # 2
    A.x.bind(B.x + C.x)  # 3
    A.x.bind(B.x or C.x)  # 4
    A.x.bind(lambda : B.x)  # 5
    A.x.bind(B.x.bind(C.x))  # 6

```

如果我们要让上述 6 种情形都能正常工作, 具体要怎么实现这个绑定机理? 这是困扰我们的问题.

下面我们先给出一个拟定方案, 然后再对上述情形中的个别做简单的补充说明.

# 拟定方案

下面的方案是理论上可行的. 暂时还来不及做. [TODO: 做好后在这里更新下状态.]

首先, `A.x` 触发 `bind` 方法的那一刻, 我们是可以捕捉到这个时刻的:

```python
class Delegator:  # class of A.x
    
    def __getattr__(self, item):
        if item == 'bind':
            # ◆◇◆ 在这里, 我们知道, A.x 打算调用 bind 方法了 ◆◇◆
            ...
        ...
```

这时候, 利用 `sys._getframe(1)` 是可以获取到上一个帧的, 同时也意味着我们是可以在这个时候拿到上一帧的 "文件名", "行号", "源代码", "上下文" (`globals` and `locals`) 等非常关键的信息.

```python
class Delegator:  # class of A.x
    
    def __getattr__(self, item):
        if item == 'bind':
            # 在这里, 我们知道, A.x 打算调用 bind 方法了
            # ◆◇◆ 获取帧信息 ◆◇◆
            info = _extract_last_frame_info(sys._getframe(1))
            ...
        ...
        

def _extract_last_frame_info(frame):
    # return filename, lineno, source_line, globals and locals.
    # ◆◇◆ PS: globals 其实不要也行, 有 locals 就可以了. ◆◇◆
    ...

```

有了这些信息以后, 我们对其稍作 "加工", 就掌握了两个重要的事情:

1. `A.x.bind(<source_code>)` 中的源代码长什么样
2. 都有哪些对象参与了此次 "事件" 的触发

    ```
    A.x.bind(B.x or C.x)  # 4
             |      |
             |      +-----------+
             +--------------+   |
                            |   |
    locals = {              |   |
        'A': <object A>,    |   |
        'B': <object B>, <--+   |
        'C': <object C>, <------+
        ...
    }
    ```

利用这两条信息, 我们可以构建出一个 lambda 函数:

```python
event = lambda: eval('A.x = B.x or C.x', locals())
```

现在到了收尾阶段, 我们需要每一个参与者对此事件 "负责". 即, 参与者的属性每发生一次变化, 都要激发一次此事件.

现在考虑有两种方法来实现这种 "信号 - 槽" 结构:

**a) 在 python 端实现**

```python
event = lambda: eval('A.x = B.x or C.x', locals())
participants = [B, C]

# 这里是概念演示
B.x.changed.connect(event)
C.x.changed.connect(event)
```

备注: 该方案不确定能不能做, 手上缺乏 `QQmlProperty.notifySignalChanged` 在 python 端如何实现的资料.

**b) 在 qml (qmlside) 端实现**

```python
from declare_pyside import qmlside

event = lambda: eval('A.x = B.x or C.x', locals())
participants = [B, C]

# 这里是概念演示
qmlside.bind(event, participants)

# qmlside.bind 会将参数进行加工后, 放在 QmlSide.qml 中进行信号绑定.
"""qml
// QmlSide.qml
// 注: 这个文件已经在程序启动时注册到 QML 的全局上下文中了, 所以这里的操作会被
// QML 运行时处理.

Item {

    ...    

    function bind(recipient, prop_name, participants, event_id) {
        eval(`
            recipient.${prop_name} = Qt.binding(() => pyside.call(
                '${event_id}', participants
            ))
        `)
    }

    ...    

}
"""
```

备注: 该方案初步认为可以实现.

# 对个别情形的补充说明

```python
from declare_pyside.widgets import Window, Item


with Window():

    with Item() as A:
        A.x = 0
        
    with Item() as B:
        B.x = 0
        
    with Item() as C:
        C.x = 0
    
    # 现在我们想让 A.x 与其他对象的 x 属性动态绑定. 当其他对象的 x 改变时, A.x 
    # 也得到更新.
    # 下面展示几种可能出现的情形 (稀有度从低到高).
    
    A.x.bind(B.x)  # 1: ◆◇◆ 未来会对这种简单情形做专门的优化 ◆◇◆
    A.x.bind(B.x + 1)  # 2: ◆◇◆ 未来会对这种简单情形做专门的优化 ◆◇◆
    A.x.bind(B.x + C.x)  # 3: ◆◇◆ 略 ◆◇◆
    A.x.bind(B.x or C.x)  # 4: ◆◇◆ 略 ◆◇◆
    A.x.bind(lambda : B.x)  # 5: ◆◇◆ 参数类型错误, 直接报错 ◆◇◆
    A.x.bind(B.x.bind(C.x))  # 6: ◆◇◆ 参数类型错误, 直接报错 ◆◇◆

```

# 参考链接

- https://zhuanlan.zhihu.com/p/56401271
