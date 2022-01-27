import socket
import threading
import subprocess
import time
import pickle


class EmpaticaServerConnectError(Exception):
    """
    Custom exception for when the socket fails to connect to the Empatica Server.
    """
    pass


class EmpaticaCommandError(Exception):
    """
    Custom exception for when an Empatica response is an error message.
    """
    pass


class EmpaticaDataError(Exception):
    """
    Custom exception for when there is an error when parsing a data message.
    """
    pass


class EmpaticaDataStreams:
    """
    Applicable data streams that can be received from the Empatica server.
    """
    ACC = b'acc'
    BAT = b'bat'
    BVP = b'bvp'
    GSR = b'gsr'
    IBI = b'ibi'
    TAG = b'tag'
    TMP = b'tmp'
    ALL_STREAMS = [b'acc', b'bat', b'bvp', b'gsr', b'ibi', b'tag', b'tmp']


def start_e4_server(exe_path):
    """
    Starts the Empatica Streaming Server.
    :param exe_path: str: full path to Empatica Streaming Server executable
    :return: None.
    """
    subprocess.Popen(exe_path)


class EmpaticaClient:
    """
    Client object to handle the socket connection to the Empatica Server.
    """

    def __init__(self):
        """
        Initializes the socket connection and starts the data reception thread.
        """
        self.waiting = False
        try:
            self.socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_conn.connect(('127.0.0.1', 28000))
        except ConnectionError as e:
            raise EmpaticaServerConnectError(e)
        self.device = None
        self.device_list = []
        self.reading_thread = None
        self.reading = True
        self.start_receive_thread()
        self.readings = 0
        self.last_error = None
        self.errors = {
            "EmpaticaServerConnectError": [],
            "EmpaticaCommandError": [],
            "EmpaticaDataError": [],
            "Other": []
        }

    def close(self):
        """
        Stops the reading thread and closes the socket.
        :return: None.
        """
        try:
            self.stop_reading_thread()
            self.socket_conn.close()
        except Exception as e:
            self.errors["Other"].append(str(e))

    def send(self, packet):
        """
        Blocking method to send a packet to the Empatica Server.
        :param packet: str command
        :return: None.
        """
        try:
            self.socket_conn.send(packet)
        except Exception as e:
            self.errors["Other"].append(str(e))

    def recv(self):
        """
        Blocking method to receive a packet from the Empatica Server.
        :return: bytes-like.
        """
        try:
            return self.socket_conn.recv(4096)
        except Exception as e:
            self.errors["Other"].append(str(e))

    def start_receive_thread(self):
        """
        Starts the receiving thread to handle responses from Empatica Server.
        :return: None.
        """
        self.reading = True
        self.reading_thread = threading.Thread(target=self.handle_reading_receive)
        self.reading_thread.start()

    # https://developer.empatica.com/windows-streaming-server-commands.html
    def handle_reading_receive(self):
        """
        Parses and handles packets received from the Empatica Server.
        :return: None.
        """
        while self.reading:
            try:
                return_bytes = self.socket_conn.recv(4096)
                return_bytes = return_bytes.split()
                if return_bytes:
                    if return_bytes[0] == b'R':
                        if b'ERR' in return_bytes:
                            self.handle_error_code(return_bytes)
                        elif b'connection' in return_bytes:
                            self.handle_error_code(return_bytes)
                        elif b'device' in return_bytes:
                            self.handle_error_code(return_bytes)
                        elif b'device_list' in return_bytes:
                            self.device_list = []
                            for i in range(4, len(return_bytes), 2):
                                if return_bytes[i + 1] == b'Empatica_E4':
                                    self.device_list.append(return_bytes[i])
                        elif b'device_connect' in return_bytes:
                            self.device.connected = True
                            self.device.start_window_timer()
                        elif b'device_disconnect' in return_bytes:
                            self.device.connected = False
                        elif b'device_subscribe' in return_bytes:
                            self.device.subscribed_streams[return_bytes[2].decode("utf-8")] = \
                                not self.device.subscribed_streams.get(return_bytes[2].decode("utf-8"))
                    elif return_bytes[0][0:2] == b'E4':
                        self.handle_data_stream(return_bytes)
            except ConnectionAbortedError as cae:
                self.last_error = str(cae)
                self.errors["Other"].append(str(cae))
                self.reading = False
                if self.device:
                    self.device.connected = False
            except ConnectionResetError as cre:
                self.last_error = str(cre)
                self.errors["Other"].append(str(cre))
                self.reading = False
                if self.device:
                    self.device.connected = False
            except ConnectionError as ce:
                self.last_error = str(ce)
                self.errors["Other"].append(str(ce))
                self.reading = False
                if self.device:
                    self.device.connected = False

    def stop_reading_thread(self):
        """
        Sets the reading thread variable to False to stop the reading thread.
        :return: None.
        """
        self.reading = False

    def handle_error_code(self, error):
        """
        Parses error code for formatting in Exception message.
        :param error: bytes-like error message.
        :return: None.
        """
        message = ""
        for err in error:
            message = message + err.decode("utf-8") + " "
        self.last_error = "EmpaticaCommandError - " + message
        self.errors["EmpaticaCommandError"].append(message)

    def handle_data_stream(self, data):
        """
        Parses and saves the data received from the Empatica Server.
        :param data: bytes-like packet.
        :return: None.
        """
        try:
            self.readings += 1
            data_type = data[0][3:]
            if data_type == b'Acc':
                self.device.acc_3d.append(float(data[2]))
                self.device.acc_3d.append(float(data[3]))
                self.device.acc_3d.append(float(data[4]))
                self.device.acc_x.append(float(data[2]))
                self.device.acc_y.append(float(data[3]))
                self.device.acc_z.append(float(data[4]))
                self.device.acc_timestamps.append(float(data[1]))
            elif data_type == b'Bvp':
                self.device.bvp.append(float(data[2]))
                self.device.bvp_timestamps.append(float(data[1]))
            elif data_type == b'Gsr':
                self.device.gsr.append(float(data[2]))
                self.device.gsr_timestamps.append(float(data[1]))
                if all(ele == 0 for ele in self.device.gsr[-self.device.wrist_sensitivity:]):
                    self.device.on_wrist = False
                else:
                    self.device.on_wrist = True
            elif data_type == b'Temperature':
                self.device.tmp.append(float(data[2]))
                self.device.tmp_timestamps.append(float(data[1]))
            elif data_type == b'Ibi':
                self.device.ibi.append(float(data[2]))
                self.device.ibi_timestamps.append(float(data[1]))
            elif data_type == b'Hr':
                self.device.hr.append(float(data[2]))
                self.device.hr_timestamps.append(float(data[1]))
            elif data_type == b'Battery':
                self.device.bat.append(float(data[2]))
                self.device.bat_timestamps.append(float(data[1]))
            elif data_type == b'Tag':
                self.device.tag.append(float(data[2]))
                self.device.tag_timestamps.append(float(data[1]))
            else:
                self.last_error = "EmpaticaDataError - " + str(data)
                self.errors["EmpaticaDataError"].append(data)
        except Exception as e:
            self.last_error = "EmpaticaDataError - " + str(data) + str(e)
            self.errors["EmpaticaDataError"].append(str(data) + str(e))

    def list_connected_devices(self):
        """
        Sends the list connected devices command to get the devices auto-connected over BLE.
        :return: None
        """
        self.socket_conn.send(b'device_list\r\n')


class EmpaticaE4:
    """
    Class to wrap the client socket connection and configure the data streams.
    """
    def __init__(self, device_name, window_size=None, wrist_sensitivity=1):
        """
        Initializes the socket connection and connects the Empatica E4 specified.
        :param device_name: str: The Empatica E4 to connect to
        :param window_size: int: The size of windows in seconds, default None
        :param wrist_sensitivity: int: The number of samples to determine if E4 is on wrist, default is one
        """
        self.wrist_sensitivity = wrist_sensitivity
        self.window_size = window_size
        self.on_wrist = False
        self.window_thread = threading.Thread(target=self.timer_thread)
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
        self.windowed_readings = []
        self.subscribed_streams = {
            "acc": False,
            "bvp": False,
            "gsr": False,
            "tmp": False,
            "tag": False,
            "ibi": False,
            "bat": False
        }

    def start_window_timer(self):
        """
        Starts the window timer thread.
        :return:
        """
        if self.window_size:
            self.window_thread.start()

    def timer_thread(self):
        """
        Thread that will split window after window elapses.
        :return:
        """
        if self.window_size:
            while self.connected:
                time.sleep(self.window_size - time.monotonic() % self.window_size)
                self.split_window()

    def split_window(self):
        """
        Splits the current dataset into window and saves it to windowed_readings.
        :return:
        """
        # Save all the readings to our window
        self.windowed_readings.append(
            (self.acc_3d[-(32*3)*self.window_size:],
             self.acc_x[-32*self.window_size:],
             self.acc_y[-32*self.window_size:],
             self.acc_z[-32*self.window_size:],
             self.acc_timestamps[-32*self.window_size:],
             self.bvp[-64*self.window_size:], self.bvp_timestamps[-64*self.window_size:],
             self.gsr[-4*self.window_size:], self.gsr_timestamps[-4*self.window_size:],
             self.tmp[-4*self.window_size:], self.tmp_timestamps[-4*self.window_size:],
             self.tag, self.tag_timestamps,
             self.ibi, self.ibi_timestamps,
             self.bat, self.bat_timestamps,
             self.hr, self.hr_timestamps)
        )
        # Clear all readings collected so far
        self.tag, self.tag_timestamps = [], []
        self.ibi, self.ibi_timestamps = [], []
        self.bat, self.bat_timestamps = [], []
        self.hr, self.hr_timestamps = [], []

    def close(self):
        """
        Closes the socket connection.
        :return: None.
        """
        self.connected = False
        self.client.close()

    def send(self, command):
        """
        Blocking method to send data to Empatica Server.
        :param command: bytes-like: data to send
        :return: None.
        """
        self.client.send(command)

    def receive(self):
        """
        Blocking method to receive data from Empatica Server.
        :return: bytes-like: packet received.
        """
        return self.client.recv()

    def connect(self, device_name, timeout=5):
        """
        Sends the connect command packet to the Empatica Server.
        :param timeout: int: seconds before EmpaticaServerConnectError raised
        :param device_name: bytes-like: Empatica E4 to connect to
        :return: None.
        """
        command = b'device_connect ' + device_name + b'\r\n'
        self.client.device = self
        self.send(command)
        start_time = time.time()
        while not self.connected:
            if time.time() - start_time > timeout:
                raise EmpaticaServerConnectError(f"Could not connect to {device_name}!")
            pass

    def disconnect(self, timeout=5):
        """
        Sends the disconnect command packet to the Empatica Server.
        :param timeout: int: seconds before EmpaticaServerConnectError raised
        :return: None.
        """
        command = b'device_disconnect\r\n'
        self.send(command)
        start_time = time.time()
        while self.connected:
            if time.time() - start_time > timeout:
                raise EmpaticaServerConnectError(f"Could not disconnect from device!")
            pass
        self.client.stop_reading_thread()

    def save_readings(self, filename):
        """
        Saves the readings currently collected to the specified filepath.
        :param filename: str: full path to file to save to
        :return: None.
        """
        if self.windowed_readings:
            with open(filename, "wb") as file:
                pickle.dump(self.windowed_readings, file)
        else:
            with open(filename, "w") as file:
                for reading in self.acc_3d:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.acc_x:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.acc_y:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.acc_z:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.acc_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.gsr:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.gsr_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.bvp:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.bvp_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.tmp:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.tmp_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.hr:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.hr_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.ibi:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.ibi_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.bat:
                    file.write(str(reading) + ",")
                file.write("\n")
                for reading in self.bat_timestamps:
                    file.write(str(reading) + ",")
                file.write("\n")

    def clear_readings(self):
        """
        Clears the readings collected.
        :return: None.
        """
        self.acc_3d, self.acc_x, self.acc_y, self.acc_z, self.acc_timestamps = [], [], [], [], []
        self.bvp, self.bvp_timestamps = [], []
        self.gsr, self.gsr_timestamps = [], []
        self.tmp, self.tmp_timestamps = [], []
        self.tag, self.tag_timestamps = [], []
        self.ibi, self.ibi_timestamps = [], []
        self.bat, self.bat_timestamps = [], []
        self.hr, self.hr_timestamps = [], []

    def subscribe_to_stream(self, stream, timeout=5):
        """
        Subscribes the socket connection to a data stream, blocks until the Empatica Server responds.
        :param timeout: int: seconds before EmpaticaServerConnectError raised
        :param stream: bytes-like: data to stream.
        :return: None.
        """
        command = b'device_subscribe ' + stream + b' ON\r\n'
        self.send(command)
        start_time = time.time()
        while not self.subscribed_streams.get(stream.decode("utf-8")):
            if time.time() - start_time > timeout:
                raise EmpaticaServerConnectError(f"Could not subscribe to {stream}!")
            pass

    def unsubscribe_from_stream(self, stream, timeout=5):
        """
        Unsubscribes the socket connection from a data stream, blocks until the Empatica Server responds.
        :param timeout: int: seconds before EmpaticaServerConnectError raised
        :param stream: bytes-like: data to stop streaming.
        :return: None.
        """
        command = b'device_subscribe ' + stream + b' OFF\r\n'
        self.send(command)
        start_time = time.time()
        while self.subscribed_streams.get(stream.decode("utf-8")):
            if time.time() - start_time > timeout:
                raise EmpaticaServerConnectError(f"Could not unsubscribe to {stream}!")
            pass

    def suspend_streaming(self):
        """
        Stops the data streaming from the Empatica Server for the Empatica E4.
        :return: None.
        """
        command = b'pause ON\r\n'
        self.send(command)

    def start_streaming(self):
        """
        Starts the data streaming from the Empatica Server for the Empatica E4.
        :return: None.
        """
        command = b'pause OFF\r\n'
        self.send(command)
