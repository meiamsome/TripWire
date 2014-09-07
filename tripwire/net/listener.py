from tripwire.hooks import ServerStartHook, ServerStopHook

class Listener(object):
    def __init__(self, server):
        self._server = server
        self._server.register_hook_handler(ServerStartHook, self.start_listening, -100)
        self._server.register_hook_handler(ServerStopHook, self.close, 0)

    def start_listening(self, hook):
        # TODO, start the listening port on a separate thread.
        pass

    def close(self, hook):
        pass