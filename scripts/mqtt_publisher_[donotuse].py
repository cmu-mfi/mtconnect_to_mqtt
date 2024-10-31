#!/usr/bin/env python3

import os
import time

import yaml
from omegaconf import OmegaConf
from ping3 import ping, verbose_ping

import requests
import xmltodict

from mqtt_spb_wrapper import MqttSpbEntityDevice

def parse_xml(xml): 
    val = xmltodict.parse(xml, encoding='utf-8')
    val = OmegaConf.create(val)
    return val

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

        data = self.get_data('current')
        components_data = data.MTConnectStreams.Streams.DeviceStream.ComponentStream
        
        for component in components_data:
            component_id = component['@componentId']
            spb_component = MqttSpbEntityDevice(group_name,
                                                edge_node_name,
                                                component_id,
                                                debug)
        # self.components[component_id] = spb_component

        # Connect to the MQTT broker --------------------------------------------
        # print("Trying to connect to broker...")
        # for component in self.components.values():
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
        
        # Ping to see if MTConnect agent is active -----------------------------------
        print("Checking if MTConnect agent is active ...")
        pinged = False
        ip = self.cfg['mtconnect']['agent_ip']
        while not pinged:
            response = ping(ip)
            if response is not None:
                pinged = True
        
        print(f"MTConnect agent at {ip} is active")      

    def publish_birth(self):
        response = self.get_data('current')
        
        for component in response.MTConnectStreams.Streams.DeviceStream.ComponentStream:
            # set attributes value
            component_id = component['@componentId']
            component_name = component['@name']
            experiment_class = self.cfg['experiment_class']
            self.components[component_id].attributes.set_value('component_name', component_name)
            self.components[component_id].attributes.set_value('experiment_class', experiment_class)
            

            # merge Events and Samples values, if both exist
            values = {}
            if 'Events' in component:
                values.update(component.Events)
            if 'Samples' in component:
                values.update(component.Samples)
            
            # set initial values            
            for data_item_list in values.values():
                for data_item in data_item_list:
                    try:
                        data_item_id = data_item['@dataItemId']
                        # data_item_prefix = 'DATA/'+data_item_id+'/'
                        for key in data_item.keys():
                                self.components[component_id].data.set_value(data_item_id+'/'+key, data_item[key])
                    except TypeError:
                        data_item_id = data_item_list['@dataItemId']
                        # data_item_prefix = 'DATA/'+data_item_id+'/'
                        for key in data_item_list.keys():
                                self.components[component_id].data.set_value(data_item_id+'/'+key, data_item_list[key])
                        break
            self.components[component_id].publish_birth()

    def get_data(self, ext: str):
        URL = self.cfg['mtconnect']['agent_url']
        response = requests.get(URL + ext)
        return parse_xml(response.text)
    
    def streamdata(self):
        response = self.get_data('sample')
        
        for component in response.MTConnectStreams.Streams.DeviceStream.ComponentStream:   
            if_break = False
            try:
                component_id = component['@componentId']      
            except TypeError:
                component = response.MTConnectStreams.Streams.DeviceStream.ComponentStream
                component_id = component['@componentId']
                if_break = True
            # merge Events and Samples values, if both exist
            values = {}
            if 'Events' in component:
                values.update(component.Events)
            if 'Samples' in component:
                values.update(component.Samples)
            
            # set initial values            
            for data_item_list in values.values():
                for data_item in data_item_list:
                    try:
                        data_item_id = data_item['@dataItemId']
                        data_item_prefix = 'DATA/'+data_item_id+'/'
                        for key in data_item.keys():
                                self.components[component_id].data.set_value(data_item_prefix+key, data_item[key])
                    except TypeError:
                        data_item_id = data_item_list['@dataItemId']
                        data_item_prefix = 'DATA/'+data_item_id+'/'
                        for key in data_item_list.keys():
                                self.components[component_id].data.set_value(data_item_prefix+key, data_item_list[key])
                        break
            self.components[component_id].publish_data()
            if if_break:
                break     

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(script_dir, 'config.yaml')
    
    with open(config_path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader) 
    
    config = OmegaConf.create(config)
    
    MTConnectToSPBDevice(config)
