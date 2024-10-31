#!/usr/bin/env python3

import os
import time

import random
import yaml
from omegaconf import OmegaConf
import xmltodict

from mqtt_spb_wrapper import MqttSpbEntityDevice

class MTConnectToSPBDevice:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.components = {}

        self.connect()
        self.publish_birth()
        try:
            while True:
                self.streamdata()
        except KeyboardInterrupt:
            print("Application interrupted by user. Exiting ...")

    def connect(self):
        group_name = self.cfg['mqtt']['group_name']
        edge_node_name = self.cfg['mqtt']['node_name']
        mqtt_host = self.cfg['mqtt']['broker_address']
        mqtt_port = int(self.cfg['mqtt']['broker_port'])
        mqtt_user = self.cfg['mqtt']['username']
        mqtt_pass = self.cfg['mqtt']['password']
        mqtt_tls_enabled = self.cfg['mqtt']['tls_enabled']
        debug = self.cfg['mqtt']['debug']
        
        components = ['c1', 'c2', 'c3']
        
        for component_id in components:
            spb_component = MqttSpbEntityDevice(group_name,
                                                edge_node_name,
                                                component_id,
                                                debug)

            _connected = False
            while not _connected:
                _connected = spb_component.connect(mqtt_host,
                                                mqtt_port,
                                                mqtt_user,
                                                mqtt_pass,
                                                mqtt_tls_enabled)
                if not _connected:
                    print("  Error, could not connect. Trying again in a few seconds ...")
                    time.sleep(3)

            self.components[component_id] = spb_component
        print(f"All components connected to broker")    

    def publish_birth(self):
        
        for component_id in self.components.keys():
            # set attributes value
            experiment_class = self.cfg['experiment_class']
            self.components[component_id].attributes.set_value('experiment_class', experiment_class)

            # set dummy data value
            input_value = { 'test_value' : -1 }
        
            for key in input_value.keys():
                self.components[component_id].data.set_value(key, input_value[key])

            self.components[component_id].publish_birth()
            print(f"Birth published for component {component_id}, test_value: {input_value['test_value']}")
    
    def streamdata(self):        
        for component_id in self.components.keys():   

            # set dummy data value
            input_value = { 'test_value' : random.randint(1, 100) }

            for key in input_value.keys():
                data_item_prefix = 'DATA/'+key
                self.components[component_id].data.set_value(data_item_prefix, input_value[key])            
                
            self.components[component_id].publish_data()

            print(f"Data published for component {component_id}, test_value: {input_value['test_value']}")
            time.sleep(1)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, '../config/config.yaml')
    
    with open(config_path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader) 
    
    config = OmegaConf.create(config)
    
    MTConnectToSPBDevice(config)