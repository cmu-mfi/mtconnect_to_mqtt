#!/usr/bin/env python3

import random

from core.mtconnect_to_spbdevice import MTConnectToSPBDevice

class DummyDataClass:        
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.component_ids = []
        self.data = {}
        self.attributes = {}
        
        self.connect()
        
    def connect(self):
        pass
    
    def get_data(self):
        self.component_ids = ['c1', 'c2', 'c3']
        for component_id in self.component_ids:
            self.data[component_id] = {}
            self.data[component_id]['test_number'] = 101
            self.attributes[component_id] = {'attr_a': random.randint(0, 100), 'attr_b': random.randint(0, 100)}
            
    def update_data(self):
        for component_id in self.component_ids:
            self.data[component_id]['test_number'] = random.randint(0, 100)

if __name__ == "__main__": 
    
    config = {}
    data_obj = DummyDataClass(config)
    
    MTConnectToSPBDevice(data_obj)
