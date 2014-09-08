from tripwire.hooks import ServerStartHook

class ComponentManager(object):
    def __init__(self, server, *args, **kwargs):
        super(ComponentManager, self).__init__(*args, **kwargs)
        self.enabled_components = {}
        self.load_on_start = ["components.netlogger.netlogger.NetLogger"]
        self._server = server
        self._server.register_hook_handler(ServerStartHook, self.on_start, -1)

    def on_start(self, hook):
        for to_load in self.load_on_start:
            from_module, component_name = to_load.rsplit('.', 1)
            module = __import__(from_module, globals(), locals(), [component_name], 0)
            component = getattr(module, component_name)
            if not issubclass(component, Component):
                raise Exception()#TODO
            else:
                #TODO: Hooks & stuff
                component(self._server).enable()


class Component(object):
    def __init__(self, server, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)
        self._server = server

    def enable(self):
        pass

    def disable(self):
        pass