from tripwire.dispatcher import HookDispatcher
from tripwire.net.listener import Listener
from tripwire.net.version1 import ClientMaintainer
from tripwire.ticker import Ticker
from tripwire.hooks import BaseHook, ServerStartHook
from tripwire.component import ComponentManager


class TripWireServer(object):

    def __init__(self):
        # Set up key components.
        self._hook_dispatcher = HookDispatcher(self)
        self._listener = Listener(self)
        self._ticker = Ticker(self)
        self._client_handler = ClientMaintainer(self)
        self._component_manager = ComponentManager(self)
        # Trigger the server start.
        self.handle_hook(ServerStartHook())

    def register_hook_handler(self, hook_type, handler, priority):
        self._hook_dispatcher.register_handler(hook_type, handler, priority)

    def handle_hook(self, hook):
        self._hook_dispatcher.handle_hook(hook)

if __name__ == '__main__':
    TripWireServer()