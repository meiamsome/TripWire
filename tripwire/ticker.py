from tripwire.hooks import ServerStartHook, ServerTickHook, ServerStopHook
from datetime import datetime, timedelta
from time import sleep

class Ticker(object):
    def __init__(self, server):
        self._going = False
        self._server = server
        self._server.register_hook_handler(ServerStartHook, self.run, -1000)
        self._server.register_hook_handler(ServerStopHook, self.stop, 0)

    def run(self, hook):
        self._going = True
        while self._going:
            current_time = datetime.now()
            self._server.handle_hook(ServerTickHook())
            sleep_time = ((current_time + timedelta(milliseconds=50)) - datetime.now()).total_seconds()
            if sleep_time > 0:
                sleep(sleep_time)

    def stop(self, hook):
        self._going = False