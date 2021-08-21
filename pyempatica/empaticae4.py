import socket
import threading
import pickle


class EmpaticaCommandError(Exception):
    pass


class EmpaticaDataError(Exception):
    pass


class EmpaticaDataStreams:
    ACC = b'acc'
    BAT = b'bat'
    BVP = b'bvp'
    GSR = b'gsr'
    IBI = b'ibi'
    TAG = b'tag'
    TMP = b'tmp'
    ALL_STREAMS = [b'acc', b'bat', b'bvp', b'gsr', b'ibi', b'tag', b'tmp']


def start_e4_server(exe_path):
    raise NotImplemented


class EmpaticaClient:
    def __init__(self):
        self.waiting = False
        self.buffer_size = 4096
        self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_conn.connect(('127.0.0.1', 28000))
        self.device = None
        self.device_list = []
        self.reading_thread = None
        self.reading = True
        self.start_receive_thread()

    def close(self):
        self.stop_reading_thread()
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
            return_bytes = return_bytes.split()
            if return_bytes[0] == b'R':
                if b'ERR' in return_bytes:
                    self.handle_error_code(return_bytes)
                elif b'connection' in return_bytes:
                    self.handle_error_code(return_bytes)
                elif b'device' in return_bytes:
                    self.handle_error_code(return_bytes)
                elif b'device_list' in return_bytes:
                    for i in range(4, len(return_bytes), 2):
                        if return_bytes[i + 1] == b'Empatica_E4':
                            self.device_list.append(return_bytes[i])
                elif b'device_connect' in return_bytes:
                    self.device.connected = True
                elif b'device_subscribe' in return_bytes:
                    self.device.subscribed_streams[return_bytes[2].decode("utf-8")] = \
                        not self.device.subscribed_streams.get(return_bytes[2].decode("utf-8"))
            elif return_bytes[0][0:2] == b'E4':
                self.handle_data_stream(return_bytes)

    def stop_reading_thread(self):
        self.reading = False

    @staticmethod
    def handle_error_code(error):
        message = ""
        for err in error:
            message = message + err.decode("utf-8") + " "
        raise EmpaticaCommandError(message)

    def handle_data_stream(self, data):
        try:
            data_type = data[0][3:]
            if data_type == b'Acc':
                self.device.acc_3d.append(float(data[2]))
                self.device.acc_3d.append(float(data[3]))
                self.device.acc_3d.append(float(data[4]))
                self.device.acc_x.append(float(data[2]))
                self.device.acc_y.append(float(data[3]))
                self.device.acc_z.append(float(data[4]))
                self.device.acc_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Bvp':
                self.device.bvp.append(float(data[2]))
                self.device.bvp_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Gsr':
                self.device.gsr.append(float(data[2]))
                self.device.gsr_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Temperature':
                self.device.tmp.append(float(data[2]))
                self.device.tmp_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Ibi':
                self.device.ibi.append(float(data[2]))
                self.device.ibi_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Hr':
                self.device.hr.append(float(data[2]))
                self.device.hr_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Battery':
                self.device.bat.append(float(data[2]))
                self.device.bat_timestamps.append(float(data[1]))
                pass
            elif data_type == b'Tag':
                self.device.tag.append(float(data[2]))
                self.device.tag_timestamps(float(data[1]))
                pass
            else:
                raise EmpaticaDataError(data)
        except:
            raise EmpaticaDataError(data)

    def list_connected_devices(self):
        self.socket_conn.send(b'device_list\r\n')


class EmpaticaE4:
    def __init__(self, device_name):
        self.client = EmpaticaClient()
        self.connected = False
        self.connect(device_name)
        while not self.connected:
            pass
        self.suspend_streaming()
        self.acc_3d, self.acc_x, self.acc_y, self.acc_z, self.acc_timestamps = [], [], [], [], []
        self.bvp, self.bvp_timestamps = [], []
        self.gsr, self.gsr_timestamps = [], []
        self.tmp, self.tmp_timestamps = [], []
        self.tag, self.tag_timestamps = [], []
        self.ibi, self.ibi_timestamps = [], []
        self.bat, self.bat_timestamps = [], []
        self.hr, self.hr_timestamps = [], []
        self.subscribed_streams = {
            "acc": False,
            "bvp": False,
            "gsr": False,
            "tmp": False,
            "tag": False,
            "ibi": False,
            "bat": False
        }

    def close(self):
        self.client.close()

    def send(self, command):
        self.client.send(command)

    def receive(self):
        return self.client.recv()

    def connect(self, device_name):
        command = b'device_connect ' + device_name + b'\r\n'
        self.send(command)
        self.client.device = self

    def disconnect(self):
        command = b'device_disconnect\r\n'
        self.send(command)

    def save_readings(self, filename):
        with open(filename, "w") as file:
            file.writelines(self.acc_3d)
            file.writelines(self.acc_x)
            file.writelines(self.acc_y)
            file.writelines(self.acc_z)
            file.writelines(self.acc_timestamps)
            file.writelines(self.gsr)
            file.writelines(self.gsr_timestamps)
            file.writelines(self.bvp)
            file.writelines(self.bvp_timestamps)
            file.writelines(self.tmp)
            file.writelines(self.tmp_timestamps)
            file.writelines(self.ibi)
            file.writelines(self.ibi_timestamps)
            file.writelines(self.hr)
            file.writelines(self.hr_timestamps)
            file.writelines(self.bat)
            file.writelines(self.bat_timestamps)
            file.writelines(self.tag)

    def clear_readings(self):
        self.acc_3d, self.acc_x, self.acc_y, self.acc_z, self.acc_timestamps = [], [], [], [], []
        self.bvp, self.bvp_timestamps = [], []
        self.gsr, self.gsr_timestamps = [], []
        self.tmp, self.tmp_timestamps = [], []
        self.tag, self.tag_timestamps = [], []
        self.ibi, self.ibi_timestamps = [], []
        self.bat, self.bat_timestamps = [], []
        self.hr, self.hr_timestamps = [], []

    def subscribe_to_stream(self, stream):
        command = b'device_subscribe ' + stream + b' ON\r\n'
        self.send(command)
        while not self.subscribed_streams.get(stream.decode("utf-8")):
            pass

    def unsubscribe_from_stream(self, stream):
        command = b'device_subscribe ' + stream + b' OFF\r\n'
        self.send(command)
        while self.subscribed_streams.get(stream.decode("utf-8")):
            pass

    def suspend_streaming(self):
        command = b'pause ON\r\n'
        self.send(command)

    def start_streaming(self):
        command = b'pause OFF\r\n'
        self.send(command)
