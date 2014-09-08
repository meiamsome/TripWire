from tripwire.hooks import BaseHook, CancellableHook


class NetHook(BaseHook):
    def __init__(self, connection_id, *args, **kwargs):
        super(NetHook, self).__init__(*args, **kwargs)
        self.connection_id = connection_id


class IncomingConnectionHook(NetHook, CancellableHook):
    def __init__(self, address, socket, *args, **kwargs):
        super(IncomingConnectionHook, self).__init__(*args, **kwargs)
        self.address = address
        self.socket = socket

class PacketReceivedHook(NetHook):
    def __init__(self, packet, *args, **kwargs):
        super(PacketReceivedHook, self).__init__(*args, **kwargs)
        self.packet = packet

class LoginAttemptHook(NetHook):
    pass