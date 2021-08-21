import socket
import threading


class EmpaticaCommandError(Exception):
    pass


class EmpaticaDataStreams:
    ACC = b'acc'
    BAT = b'bat'
    BVP = b'bvp'
    GSR = b'gsr'
    IBI = b'ibi'
    TAG = b'tag'
    TMP = b'tmp'


class EmpaticaServerReturnCodes:
    COMMAND_SUCCESS = 0
    NO_DEVICES_FOUND = 1


def start_e4_server(exe_path):
    raise NotImplemented


class EmpaticaClient:
    def __init__(self):
        self.buffer_size = 4096
        self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_conn.connect(('127.0.0.1', 28000))
        self.device = None
        self.device_list = []
        self.reading_thread = None
        self.reading = False

    def close(self):
        self.socket_conn.close()

    def send(self, packet):
        self.socket_conn.send(packet)

    def recv(self):
        return self.socket_conn.recv(4096)

    def start_receive_thread(self):
        self.reading = True
        self.reading_thread = threading.Thread(target=self.handle_reading_receive)
        self.reading_thread.start()

    def handle_reading_receive(self):
        while self.reading:
            return_bytes = self.socket_conn.recv(4096)
            print(return_bytes)

    def stop_reading_thread(self):
        self.reading = False

    @staticmethod
    def handle_error_code(error):
        message = ""
        for err in error:
            message = message + err.decode("utf-8")
        raise EmpaticaCommandError(message)

    def list_connected_devices(self):
        self.socket_conn.send(b'device_list\r\n')
        return_bytes = self.socket_conn.recv(4096)
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'device_list':
            for i in range(4, len(return_bytes), 2):
                if return_bytes[i + 1] == b'Empatica_E4':
                    self.device_list.append(return_bytes[i].decode("utf-8"))
            if len(self.device_list) == 0:
                return EmpaticaServerReturnCodes.NO_DEVICES_FOUND
            else:
                return EmpaticaServerReturnCodes.COMMAND_SUCCESS
        else:
            print("Something went wrong, return:", return_bytes)
            return False


class EmpaticaE4:
    def __init__(self, device_name):
        self.client = EmpaticaClient()
        if self.connect(device_name) == EmpaticaServerReturnCodes.COMMAND_SUCCESS:
            self.suspend_streaming()
        self.acc_3d, self.acc_x, self.acc_y, self.acc_z, self.acc_timestamps = [], [], [], [], []
        self.bvp, self.bvp_timestamps = [], []
        self.gsr, self.gsr_timestamps = [], []
        self.tmp, self.tmp_timestamps = [], []
        self.tag, self.tag_timestamps = [], []
        self.ibi, self.ibi_timestamps = [], []
        self.bat, self.bat_timestamps = [], []
        self.hr, self.hr_timestamps = [], []

    def send(self, command):
        self.client.send(command)

    def receive(self):
        return self.client.recv()

    def connect(self, device_name):
        command = b'device_connect ' + device_name + b' ON\r\n'
        self.send(command)
        return_bytes = self.receive()
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'device_connect':
            if return_bytes[3] == b'OK':
                self.client.device = self
                return EmpaticaServerReturnCodes.COMMAND_SUCCESS
            else:
                self.client.handle_error_code(return_bytes[4:-1])

    def disconnect(self):
        command = b'device_disconnect\r\n'
        self.send(command)
        return_bytes = self.receive()
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'device_disconnect':
            if return_bytes[3] == b'OK':
                return EmpaticaServerReturnCodes.COMMAND_SUCCESS
            else:
                self.client.handle_error_code(return_bytes[4:-1])

    def save_readings(self, filename):
        raise NotImplemented

    def grab_window(self):
        raise NotImplemented

    def clear_readings(self):
        raise NotImplemented

    def subscribe_to_stream(self, stream):
        command = b'device_subscribe ' + stream + b' ON\r\n'
        self.send(command)
        return_bytes = self.receive()
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'device_subscribe':
            if return_bytes[2] == stream:
                if return_bytes[3] == b'OK':
                    return EmpaticaServerReturnCodes.COMMAND_SUCCESS
                else:
                    self.client.handle_error_code(return_bytes[4:-1])

    def unsubscribe_from_stream(self, stream):
        command = b'device_subscribe ' + stream + b' OFF\r\n'
        self.send(command)
        return_bytes = self.receive()
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'device_subscribe':
            if return_bytes[2] == stream:
                if return_bytes[3] == b'OK':
                    return EmpaticaServerReturnCodes.COMMAND_SUCCESS
                else:
                    self.client.handle_error_code(return_bytes[4:-1])

    def suspend_streaming(self):
        command = b'pause ON\r\n'
        self.send(command)
        return_bytes = self.receive()
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'pause':
            if return_bytes[2] == b'ERR':
                self.client.handle_error_code(return_bytes[3:-1])
            else:
                self.client.stop_reading_thread()
                return EmpaticaServerReturnCodes.COMMAND_SUCCESS

    def start_streaming(self):
        command = b'pause OFF\r\n'
        self.send(command)
        return_bytes = self.receive()
        return_bytes = return_bytes.split()
        if return_bytes[0] == b'R' and return_bytes[1] == b'pause':
            if return_bytes[2] == b'ERR':
                self.client.handle_error_code(return_bytes[3:-1])
            else:
                self.client.start_receive_thread()
                return EmpaticaServerReturnCodes.COMMAND_SUCCESS
