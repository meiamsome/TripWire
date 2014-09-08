from threading import Thread, RLock
from tripwire.hooks import ServerTickHook, ServerStopHook
from tripwire.net.packet import Packet
from tripwire.net.hooks import PacketReceivedHook, IncomingConnectionHook
from Queue import Queue, Empty
import socket


class ClientMaintainer(object):
    def __init__(self, server):
        self._server = server
        self._server.register_hook_handler(IncomingConnectionHook, self.incoming_connection_handler, -100)
        self._server.register_hook_handler(ServerStopHook, self.disconnect_all, -100)
        self._connections = {}

    def incoming_connection_handler(self, hook):
        if hook.is_cancelled():
            hook.socket.close()
        else:
            #TODO: Make it so that the net handler is configurable?
            self._connections[hook.connection_id] = ClientHandler(hook.connection_id, self._server,
                                                                  hook.address, hook.socket)

    def disconnect_all(self, hook):
        pass
        # TODO for each connection broadcast DisconnectPacket


class ClientHandler(object):
    def __init__(self, connection_id, server, address, connection):
        self.connection_id = connection_id
        self.address = address
        self.connection = connection
        self._from_client = Queue()
        # Used to send shutdown request or enable encoding request
        self._to_client = Queue()
        self._thread = Thread(group=None, target=self._threaded_handle, name=None, args=(connection,))
        self._thread.start()
        server.register_hook_handler(ServerTickHook, self.receive_packets, 0)
        self._server = server

    def receive_packets(self, hook):
        if self._thread.is_alive():
            try:
                while True:
                    full_packet = self._from_client.get_nowait()
                    number, data_start = self._decode_varint(full_packet)
                    packet = Packet(packet_id=number, data=full_packet[data_start:])
                    self._server.handle_hook(PacketReceivedHook(packet, self.connection_id))
            except Empty:
                pass
        else:
            pass
            #TODO report connection drop

    def _threaded_handle(self, connection):
        connection.settimeout(1.0)
        decoder = None
        to_pass_up = []
        incoming_buffer = ""
        while True:
            try:
                data = self._to_client.get_nowait()
            except Empty:
                pass
            else:
                if data is None:
                    break
                else:
                    decoder = data
            if to_pass_up:
                for x in to_pass_up:
                    self._from_client.put_nowait(x)
                to_pass_up = []
            try:
                new_buffer = connection.recv(4096)
            except socket.timeout:
                pass
            else:
                if decoder is not None:
                    new_buffer = decoder.decode(new_buffer)
                incoming_buffer += new_buffer
                try:
                    count, end = self._decode_varint(incoming_buffer)
                except TypeError:
                    pass
                else:
                    if end + count < len(incoming_buffer):
                        to_pass_up.append(incoming_buffer[end:end+count])
                        incoming_buffer = incoming_buffer[end + count:]
        connection.close()

    def _decode_varint(self, stream):
        num = 0
        chars = 0
        for c in stream:
            val = ord(c)
            num += (val & 127) << 7*chars
            chars += 1
            if not val & 128:
                return num, chars
        raise TypeError("Could not decode a varint.")