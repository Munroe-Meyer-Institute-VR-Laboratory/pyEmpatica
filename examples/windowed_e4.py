from pyempatica.empaticae4 import EmpaticaClient, EmpaticaE4, EmpaticaDataStreams, EmpaticaServerConnectError
import time


try:
    client = EmpaticaClient()
    print("Connected to E4 Streaming Server...")
    client.list_connected_devices()
    print("Listing E4 devices...")
    time.sleep(1)
    if len(client.device_list) != 0:
        e4 = EmpaticaE4(client.device_list[0], window_size=5, wrist_sensitivity=2)
        if e4.connected:
            print("Connected to", client.device_list[0], "device...")
            for stream in EmpaticaDataStreams.ALL_STREAMS:
                e4.subscribe_to_stream(stream)
            print("Subscribed to all streams, starting streaming...")
            e4.start_streaming()
            for i in range(0, 1000):
                time.sleep(1)
                if not e4.on_wrist:
                    print("E4 is not on wrist, please put it on!")
                if e4.client.last_error:
                    print("Error encountered:", e4.client.last_error)
                    break
            e4.suspend_streaming()
            e4.disconnect()
            e4.close()
            print("E4 Errors")
            for key in e4.client.errors:
                print("\t", key, ":", e4.client.errors[key])
            print("E4 connection closed, saving readings...")
            e4.save_readings("readings.pkl")
            print("Readings saved to readings.pkl...")
        else:
            print("Could not connect to Empatica E4:", client.device_list[0])
    client.close()
    print("Cleaning up connections...")
except EmpaticaServerConnectError:
    print("Failed to connect to server, check the the E4 Streaming Server is open and connected to the BLE dongle.")
