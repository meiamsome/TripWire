from threading import Thread
from tripwire.hooks import ServerTickHook, ServerStopHook
from tripwire.net.packet import Packet
from tripwire.net.hooks import PacketReceivedHook, IncomingConnectionHook, PacketSendHook
from Queue import Queue, Empty
import socket


class ClientMaintainer(object):
    def __init__(self, server):
        self._server = server
        self._server.register_hook_handler(IncomingConnectionHook, self.incoming_connection_handler, -100)
        self._server.register_hook_handler(ServerStopHook, self.disconnect_all, -100)
        self._server.register_hook_handler(PacketSendHook, self.send_packet, -100)
        self._server.register_hook_handler(ServerTickHook, self.receive_packets, 0)
        self._connections = {}
        self._from_queue = Queue()

    def incoming_connection_handler(self, hook):
        if hook.is_cancelled():
            hook.socket.close()
        else:
            #TODO: Make it so that the net handler is configurable?
            self._connections[hook.connection_id] = ClientHandler(hook.connection_id, self._server,
                                                                  hook.address, hook.socket, self._from_queue)

    def receive_packets(self, hook):
        try:
            while True:
                connection_id, full_packet = self._from_queue.get_nowait()
                number, data_start = _decode_varint(full_packet)
                packet = Packet(packet_id=number, data=full_packet[data_start:])
                self._server.handle_hook(PacketReceivedHook(packet, connection_id))
        except Empty:
            pass

    def send_packet(self, hook):
        try:
            handler = self._connections[hook.connection_id]
        except KeyError:
            pass
        else:
            handler.send_packet(hook.packet)

    def disconnect_all(self, hook):
        pass
        # TODO for each connection broadcast DisconnectPacket


class ClientHandler(object):
    def __init__(self, connection_id, server, address, connection, from_queue):
        self.connection_id = connection_id
        self.address = address
        self.connection = connection
        # Used to send shutdown request or enable encoding request
        self._to_client = Queue()
        self._thread = Thread(group=None, target=self._threaded_handle, name=None,
                              args=(connection_id, connection, from_queue, self._to_client))
        self._thread.start()
        self._encoder = None
        self._server = server

    def _threaded_handle(self, connection_id, connection, from_queue, to_queue):
        connection.settimeout(1.0)
        decoder = None
        to_pass_up = []
        incoming_buffer = ""
        outgoing_buffer = ""
        while True:
            try:
                data = to_queue.get_nowait()
            except Empty:
                pass
            else:
                if data is None:
                    break
                elif data[0] == 'decoder':
                    decoder = data
                    incoming_buffer = decoder.decode(incoming_buffer)
                elif data[0] == 'packet':
                    outgoing_buffer += data[1]
            if to_pass_up:
                for x in to_pass_up:
                    from_queue.put((connection_id, x))
                to_pass_up = []
            if outgoing_buffer:
                sent = connection.send(outgoing_buffer)
                outgoing_buffer = outgoing_buffer[sent:]
            try:
                new_buffer = connection.recv(4096)
            except socket.timeout:
                pass
            else:
                if decoder is not None:
                    new_buffer = decoder.decode(new_buffer)
                incoming_buffer += new_buffer
                try:
                    count, end = _decode_varint(incoming_buffer)
                except TypeError:
                    pass
                else:
                    if end + count < len(incoming_buffer):
                        to_pass_up.append(incoming_buffer[end:end+count])
                        incoming_buffer = incoming_buffer[end + count:]
        connection.close()

    def send_packet(self, packet):
        to_send = _encode_varint(packet.packet_id) + packet.data
        to_send = _encode_varint(len(to_send)) + to_send
        if self.__encoder is not None:
            to_send = self._encoder.encode(to_send)
        self._to_client.put(('packet', to_send))

def _decode_varint(stream):
    num = 0
    chars = 0
    for c in stream:
        val = ord(c)
        num += (val & 127) << 7*chars
        chars += 1
        if not val & 128:
            return num, chars
    raise TypeError("Could not decode a varint.")

def _encode_varint(number):
    if number == 0:
        return chr(0)
    word = ""
    while number > 0:
        cur = number & 127
        number >>= 7
        if number:
            cur |= 128
        word += chr(cur)
    return word
