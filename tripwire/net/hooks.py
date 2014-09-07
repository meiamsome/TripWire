from tripwire.hooks import BaseHook, CancellableHook


class NetHook(BaseHook):
    pass


class IncomingConnection(NetHook, CancellableHook):
    def __init__(self, address, socket):
        super(IncomingConnection, self).__init__()
        self.address = address
        self.socket = socket


class LoginAttemptHook(NetHook):
    pass