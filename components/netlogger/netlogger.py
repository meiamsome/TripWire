from __future__ import print_function
from tripwire.component import Component
from tripwire.net.hooks import NetHook

class NetLogger(Component):
    def enable(self):
        print("NetLogger enabled.")
        self.get_server().register_hook_handler(NetHook, lambda x: print(x.connection_id, x), -10)