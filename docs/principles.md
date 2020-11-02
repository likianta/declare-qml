# composer 设计思想

1. 完全的视图逻辑分离

```pyml
comp Rectangle:
    style:
        width: round(id.child.width * 2)
        #      ^ 由 Python 计算出结果, 赋值给 width 属性.
        #        相当于: 
        #           width: PyComp.eval('round({PyComp.ids["child"].width} * 2)')
    Rectangle: @child
        pass
```
