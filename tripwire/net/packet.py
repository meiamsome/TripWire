class Packet(object):
    def __init__(self, packet_id, data):
        super(Packet, self).__init__()
        self.packet_id = packet_id
        self.data = data