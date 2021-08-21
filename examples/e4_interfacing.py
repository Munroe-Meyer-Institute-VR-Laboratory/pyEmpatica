from pyempatica.empaticae4 import EmpaticaClient, EmpaticaE4, EmpaticaDataStreams
import time


client = EmpaticaClient()
client.list_connected_devices()
time.sleep(1)
if len(client.device_list) != 0:
    e4 = EmpaticaE4(client.device_list[0])
    if e4.connected:
        for stream in EmpaticaDataStreams.ALL_STREAMS:
            e4.subscribe_to_stream(stream)
        e4.start_streaming()
        time.sleep(10)
        e4.suspend_streaming()
        e4.disconnect()
        e4.close()
        e4.save_readings("readings.txt")
    else:
        print("Could not connect to Empatica E4:", client.device_list[0])
