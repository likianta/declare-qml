# 问题一览

- `anchors.center_in`, `anchors.fill` 不符合 `AnchorsDelegator` 当前处理范式
- clicked 信号 "断流" 现象
- dragging 延迟明显
- `X.font.pixel_size += 1` 需要重写 `QmlSideProp.__add__` 的方法, 类似的魔术方法还有很多
- `A.font.pixel_size = B.font.pixel_size` 受当前机制所限, 只能以动态绑定的形式存在
  - 备忘: 简化 `PropDelegatorC` 的 `__get_subprop__` 和 `__set_subprop__` 的行为可以解决此问题, 但不清楚是否会造成其他影响
- states, transitions 的实现困难
- Component 的实现困难
- `Binding on x`, `NumberAnimation on opacity` 语法实现困难
