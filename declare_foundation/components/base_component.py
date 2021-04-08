from ..context_manager import context, parent, this
from ..context_manager.uid_system import UID, gen_id, id_ref


class BaseComponent:
    level: int
    uid: UID
    
    # parent: None
    # children: list['BaseComponent']
    
    __exit_lock: int
    
    #   see usage at `self.__exit__`
    #   see working principle at `ExitLockCount:docstring:作用机制`
    
    def build(self):
        """
        build self contained components (aka children components) within self's
        context.
        
        Examples:
            # xxx/address_bar.py
            class AddressBar(Item):  # Item inherits BaseComponent
                def build(self):
                    with Input() as inp:
                        inp.anchors.center = self.center
            # xxx/home.py
            with Windows() as win:
                from .addressbar import AddressBar
                with AddressBar() as addr_bar:
                    addr_bar.anchors.bind(
                        win.left, win.top, win.right, None
                    )
            
            # it equals to below
            # xxx/home.py
            with Windows() as win:
                # cons: cannot import as an individual and reusable module
                with Item() as addr_bar:
                    addr_bar.anchors.bind(
                        win.left, win.top, win.right, None
                    )
                    with Input() as inp:
                        inp.anchors.center = addr_bar.center
        """
        pass
    
    def __enter__(self):
        # self.parent = None
        # self.children = []
        global _com_exit_lock
        self.__exit_lock = _com_exit_lock.fetch_lock()
        
        # for now, `this` keyword represents 'the last' component (usually it
        # means 'parent' component), so we get the last component's real body
        # by `this.represents`
        last_com = this.represents  # type: [BaseComponent, None]
        
        self.level = last_com.level + 1 if last_com is not None else 0
        self.uid = gen_id(self.level)
        
        context.update(self.uid, self.level, self, last_com)
        #   after `context.update`, `this` and `parent` now work as expected.
        #   i.e. now `this` represents `self`, and `parent` represents `last_com`
        
        self._enter_extra()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """ 将 this, parent 分别指向 parent 和 grand_parent. """
        # self._exit_lock
        #   0: exitable
        #   >0: not exitable for now, we will decrease `self._exit_lock` count
        #       and waiting for the next call
        if self.__exit_lock > 0:
            self.__exit_lock -= 1
            return
        
        self.build()
        
        self._exit_extra(this.represents, parent.represents)
        
        this.point_to(id_ref[(pid := self.uid.parent_id)])
        parent.point_to(id_ref[pid.parent_id] if pid else None)

    def _enter_extra(self):
        raise NotImplementedError

    def _exit_extra(self, child_com, parent_com):
        """
        Caller:
            self.__exit__
            
        Examples:
            declare-qt:
                if parent_com is not None:
                    child_com.setParent(parent_com)
            declare-justpy:
                if parent_com is not None:
                    child_com.add_to(parent_com)
        """
        raise NotImplementedError


class Build:
    """
    Examples:
        def add_main_text():
            with Div() as div:
                with Text() as text:
                    return text
                    
        with WebPage() as page:
            with Build(add_main_text) as txt:
                ...
    """
    
    def __init__(self, build_func, *args, **kwargs):
        self._build_func = lambda: build_func(*args, **kwargs)
        self._view = None
    
    def __enter__(self):
        global _com_exit_lock
        _com_exit_lock.put_a_lock(1)
        #   see `ExitLockCount:docstring:作用机制`
        
        self._view = self._build_func()
        if self._view is None:
            self._view = this.represents
        assert self._view is not None
        
        return self._view
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._view.__exit__(exc_type, exc_val, exc_tb)


class ComponentExitLock:
    """
    作用机制:
        `BaseComponent` 在调用 `__enter__` 时, 会获取一个 "退出锁":
            BaseComponent.__enter__(self):
                global _com_exit_lock
                self._exit_lock = _com_exit_lock.fetch_lock()
                ...
        该锁是一个大于等于 0 的整数. 通常来说, 它的值只有两种情况: 0 或者 1.
        当退出锁的值是 0 时, `BaseComponent` 调用 `__exit__` 时可以正常退出; 当
        值为 1 时, 第一次调用 `__exit__` 时会被阻止正常退出, 此时退出锁 -= 1 (值
        变成 0); 第二次调用 `__exit__` 时才可以正常退出.
        
        为什么要阻止一次正常退出呢? 目的就是 "延缓" 正常退出机制的发生.
        如下示例:
            def some_view():
                with Text() as txt:
                    return txt  # [A]
            
            with WebPage() as page:
                with Build(some_view) as view:
                    pass
                    with Div() as div:
                        pass  # [B]
            
            当运行到 `[A]` 时, `txt` 会退出. 但我们希望的是, 在执行到 `[B]` 位置
            之后, `txt` 才退出.
            为了阻止 `txt` 在 `[A]` 位置就退出, 那么就试图让 `txt` 在 `[A]` 位置
            退出时阻止它的正常退出机制. 因此, `Build.__enter__` 就是做了这件事:
            1. 在 `txt.__enter__` 之前, 告诉 `ComponentExitLock` 要给 `txt` 加一
                个值为 1 的退出锁
            2. 在 `txt.__enter__` 时, `txt` 获取了这个锁
            3. 在 `txt` 执行到 `[A]`, `txt` 第一次调用 `__exit__`, 由于 `txt` 的
                退出锁的存在, 导致 `txt` 没有完成正常退出操作. 此时 `this` 指针
                仍然留在 `txt` (也就是说 with 的上下文环境仍然处于 `txt` 范围)
            4. 然后, `div` 在 `txt` 的上下文环境下, 正确执行它的 `__enter__` 操
                作
            5. `div` 在 `[B]` 位置执行完 `__exit__` 后, `Build(some_view)` 也开
                始触发 `Build.__exit__`, 在 `Build.__exit__` 中, `Build` 会主动
                再调用一次 `txt.__exit__`. 这次, `txt.__exit__` 就可以完成正常的
                退出操作了
    """
    
    _count = 0
    
    def fetch_lock(self):
        """ this is a one-off method, only the nearest caller could fetch the
            specific lock which been put by someone through `ComponentExitLock
            .put_a_lock`, then the else could only fetch a default lock.
        """
        out = self._count
        self.reset_lock()
        return out
    
    def reset_lock(self):
        self._count = 0
    
    def put_a_lock(self, count=1):
        self._count = count


_com_exit_lock = ComponentExitLock()
