import socketio


def start_e4_server(exe_path):
    raise NotImplemented


class EmpaticaClient:
    def __init__(self):
        self.socket_conn = socketio.Client()
        self.socket_conn.connect('http://127.0.0.1:28000')
        print('my sid is ', self.socket_conn.sid)
        self.device = None

    def send(self):
        raise NotImplemented

    def list_connected_devices(self):
        raise NotImplemented


class EmpaticaE4:
    def __init__(self, device_name):
        self.client = EmpaticaClient()

    def connect(self):
        raise NotImplemented

    def disconnect(self):
        raise NotImplemented

    def save_readings(self):
        raise NotImplemented

    def grab_window(self):
        raise NotImplemented

    def clear_readings(self):
        raise NotImplemented

    def subscribe_to_stream(self, stream):
        raise NotImplemented

    def unsubscribe_from_stream(self, stream):
        raise NotImplemented

    def suspend_streaming(self):
        raise NotImplemented

    def start_streaming(self):
        raise NotImplemented


emp = EmpaticaClient()