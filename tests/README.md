## Test Status

| Files              | Status       | Date Tested | Notes         |
| ------------------ | ------------ | ------------| --------------|
| `test_mtconnect.py`| works ✔      | 10.31.24    | Saves MTConnect current/probe/sample data in a .yaml file              |
| `spb_listener.py`  | works ✔      | 10.27.24    | Prints birth/data/death messages published to the broker |
| `test_mqtt_1.py`   | works ✔      | 10.27.24    | Successfully publishes to mqtt broker, and populates tree and values in PI |
| `test_mqtt_2.py`   | works ✔      | 10.27.24    | Tests core class MTConnectToSPBDevice. Same results as `test_mqtt_1.py` |
| `test_mqtt_3.py`   | works ✔ <br> needs more thorough testing | 10.27.24    | Tests core class MTConnect. |