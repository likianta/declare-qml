# 三种形式的属性代理

## `PropDelegatorA`

在内部以 `QObject.property(name)` 的方式返回属性值.

适用于允许通过 `QObject.property(name)` 访问的对象. 包括:

- 所有可转化为 python 基本类型的属性. 例如: x (-> float), y (-> float), text (-> str) 等
- 所有可转化为 `QtCore.*` 类型的属性. 例如: font (-> QFont), childrenRect (-> QRectF) 等

## `PropDelegatorB`

在内部以 `QQmlProperty(qobj, name).read()` 的方式返回属性值.

适用于不可通过 `QObject.property(name)` 访问的对象. 包括:

- border
- [TODO:待补充]
- ...

## `PropDelegatorC`

无法通过上述任何一种代理方式访问的属性. 但可以通过 qmlside 的 javascript 代码完成.

这里特指 anchors.



