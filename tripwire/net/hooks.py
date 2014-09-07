from tripwire.hooks import BaseHook


class NetHook(BaseHook):
    pass


class IncomingConnection(NetHook):
    def __init__(self, socket):
        self.socket = socket


class LoginAttemptHook(NetHook):
    pass