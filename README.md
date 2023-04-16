# pyEmpatica

### Parties Involved
Institution: Munroe Meyer Institute in the University of Nebraska Medical Center<br>
Laboratory: Virtual Reality Laboratory<br>
Advisor: Dr. James Gehringer<br>
Developer: Walker Arce<br>

### Motivation
This Python library was written to facilitate biometric data collection from an Empatica E4.  It also includes windowed sample collection, threaded error handling, and on-wrist detection.

### Installation
This library is available for installation over pip using:
`pip install pyEmpatica`

For developers, clone this repository, cd into the directory using either your virtual environment or your local environment, and run:
`python setup.py install`

To actually utilize this library the Empatica Streaming Server is required, meaning this library is only compatible with Windows systems.

### Usage
As of version 1.0.3 of the E4 Streaming Server, it seems there are issues with connecting the Empatica E4 for data collection.  Follow [this](https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyEmpatica/issues/1#issuecomment-1510454468) workaround to alleviate this issue. 

```
from pyempatica import EmpaticaClient, EmpaticaE4, EmpaticaDataStreams, EmpaticaServerConnectError
import time


try:
    client = EmpaticaClient()
    print("Connected to E4 Streaming Server...")
    client.list_connected_devices()
    print("Listing E4 devices...")
    time.sleep(1)
    if len(client.device_list) != 0:
        e4 = EmpaticaE4(client.device_list[0])
        if e4.connected:
            print("Connected to", str(client.device_list[0]), "device...")
            for stream in EmpaticaDataStreams.ALL_STREAMS:
                e4.subscribe_to_stream(stream)
            print("Subscribed to all streams, starting streaming...")
            e4.start_streaming()
            for i in range(0, 10):
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
            e4.save_readings("readings.txt")
            print("Readings saved to readings.txt...")
        else:
            print("Could not connect to Empatica E4:", client.device_list[0])
    client.close()
    print("Cleaning up connections...")
except EmpaticaServerConnectError:
    print("Failed to connect to server, check that the E4 Streaming Server is open and connected to the BLE dongle.")

```

Before running this script, ensure the Empatica Streaming Server is up and running.  This library is currently only compatible with Windows due to the Streaming Server dependency.

### Citation
```
@misc{Arce_pyEmpatica_2021,
      author = {Arce, Walker and Gehringer, James},
      month = {8},
      title = {{pyEmpatica}},
      url = {https://github.com/Munroe-Meyer-Institute-VR-Laboratory/pyEmpatica},
      year = {2021}
}
```
