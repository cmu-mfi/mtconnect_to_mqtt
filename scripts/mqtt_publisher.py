from core.mtconnect import MTConnect
from core.mtconnect_to_spbdevice import MTConnectToSPBDevice


if __name__ == "__main__": 
    
    data_obj = MTConnect()
    
    MTConnectToSPBDevice(data_obj)