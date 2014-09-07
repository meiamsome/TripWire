
class BaseHook(object):
    pass


class CancellableHook(object):
    def __init__(self):
        super(CancellableHook, self).__init__()
        self._is_cancelled = False

    def is_cancelled(self):
        return self._is_cancelled

    def set_cancelled(self, status=True):
        self._is_cancelled = status


class ServerStartHook(BaseHook):
    pass


class ServerStopHook(BaseHook):
    pass


class ServerTickHook(BaseHook):
    pass