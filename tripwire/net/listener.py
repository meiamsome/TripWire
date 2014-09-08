import socket

from tripwire.hooks import ServerStartHook, ServerStopHook, ServerTickHook
from tripwire.net.hooks import IncomingConnectionHook
from tripwire.net.version1 import ClientHandler

class Listener(object):
    def __init__(self, server):
        self._server = server
        self._server.register_hook_handler(ServerStartHook, self.start_listening, 0)
        self._server.register_hook_handler(ServerTickHook, self.accept, 0)
        self._server.register_hook_handler(ServerStopHook, self.close, 0)
        self._socket = None
        self._connection_count = 0

    def start_listening(self, hook):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(1.0)
        # TODO: Move to configuration
        self._socket.bind(("0.0.0.0", 25565))
        self._socket.listen(20)

    def accept(self, hook):
        try:
            connection, address = self._socket.accept()
        except socket.timeout:
            pass
        else:
            self._connection_count += 1
            self._server.handle_hook(IncomingConnectionHook(address, connection, self._connection_count))

    def close(self, hook):
        if self._socket is None:
            self._socket.close()