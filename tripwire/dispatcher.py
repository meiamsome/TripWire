from tripwire.hooks import BaseHook
from types import FunctionType, LambdaType, MethodType, IntType
from tripwire.net.hooks import NetHook

class HookDispatcher(object):
    def __init__(self, server):
        self._hook_handlers = dict()

    def register_handler(self, hook_type, handler, priority):
        if not issubclass(hook_type, BaseHook):
            raise TypeError("Hooks must extend the BaseHook type.")
        if not isinstance(handler, (FunctionType, LambdaType, MethodType)):
            raise TypeError("Hook Handlers must be a function.")
        if not isinstance(priority, IntType):
            raise TypeError("Priority must be an Int.")
        try:
            hooks = self._hook_handlers[hook_type]
            for position in xrange(len(hooks)):
                if hooks[position][0] < priority:
                    break
            else:
                position += 1
            hooks.insert(position, (priority, handler))
        except KeyError:
            self._hook_handlers[hook_type] = [(priority, handler)]


    def handle_hook(self, hook):
        if not isinstance(hook, BaseHook):
            raise TypeError("Hooks must extend the BaseHook type.")
        monitors = []
        for hook_type in type(hook).mro():
            try:
                handlers = self._hook_handlers[hook_type]
            except KeyError:
                pass
            else:
                for handler in handlers:
                    if handler[0] >= 0:
                        handler[1](hook)
                    else:
                        monitors.append(handler[1])
        for monitor in monitors:
            monitor(hook)