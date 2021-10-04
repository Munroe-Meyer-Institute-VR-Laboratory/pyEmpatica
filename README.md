# pyEmpatica

### Parties Involved
Institution: Munroe Meyer Institute in the University of Nebraska Medical Center<br>
Laboratory: Virtual Reality Laboratory<br>
Advisor: Dr. James Gehringer<br>
Developer: Walker Arce<br>

### Motivation
This Python library was written to facilitate biometric data collection from an Empatica E4.  It also includes windowed sample collection, threaded error handling, and on-wrist detection.

### Installation
Clone this repository, cd into the directory using either your virtual environment or your local environment, and run:
`python setup.py install`

### Usage
```
from pyempatica.empaticae4 import EmpaticaClient, EmpaticaE4, EmpaticaDataStreams, EmpaticaServerConnectError
import time


try:
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
    client.close()
except EmpaticaServerConnectError:
    print("Failed to connect to server, check the the E4 Streaming Server is open and connected to the BLE dongle.")
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
