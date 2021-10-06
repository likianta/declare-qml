def _get_authorized_props(cls) -> str:
    for x in cls.__annotations__:
        if not x.startswith('_'):
            yield x


class AuthorizedProps:
    """
    Notes.zh-CN:
        所有继承本类的子类, 如果该子类属于 Mixin 类型, 则必须将本类放在第一继承
        位置. 否则将导致 [MARK][1] 发生异常, 进而导致 [MARK][2] 引发断言错误.
        
    Notes:
        All subclasses that inherit from this class, if the subclass is a Mixin
        type, it must place AuthorizedProps in its first Mixin position.
        Otherwise [MARK][1] will match a wrong baseclass, then [MARK][2] will
        raise an AssertionError.
        
        [1]: `<child_class>.<classmethod:get_authorized_props>.<while_loop>
             .<var:temp_cls>.<code:'temp_cls = temp_cls.__base__'>`
        [2]: `<child_class>.<classmethod:get_authorized_props>.<while_loop>
             .<code:assert>`
    """
    
    @classmethod
    def get_authorized_props(cls) -> tuple[str, ...]:
        out = []
        temp_cls = cls
        while temp_cls.__name__ != 'AuthorizedProps':
            assert issubclass(temp_cls, AuthorizedProps)
            out.extend(_get_authorized_props(temp_cls))
            temp_cls = temp_cls.__base__
        return tuple(out)


class TextProps(AuthorizedProps):
    anchors: object
    height: float
    text: str
    width: float
    x: float
    y: float
