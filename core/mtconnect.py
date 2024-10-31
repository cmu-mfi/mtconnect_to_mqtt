import os
import yaml
import xmltodict
import omegaconf
from omegaconf import OmegaConf
from ping3 import ping, verbose_ping
import requests

class MTConnect:        
    def __init__(self) -> None:
        
        # READ CONFIG FROM FILE
        script_dir = os.path.dirname(os.path.realpath(__file__))
        config_path = os.path.join(script_dir, '../config/config.yaml')
        
        with open(config_path, 'r') as file:
            config = yaml.load(file, Loader=yaml.FullLoader) 
        
        cfg = OmegaConf.create(config)        
        self.cfg = cfg
        
        # DATA MEMBER INITIALIZATION
        self.component_ids = []
        self.data = {}
        self.attributes = {}
        
        # CHECK IF MTCONNECT AGENT IS ACTIVE
        self.connect()
        
    def connect(self):
        # Ping to see if MTConnect agent is active -----------------------------------
        print("Checking if MTConnect agent is active ...")
        pinged = False
        ip = self.cfg['mtconnect']['agent_ip']
        while not pinged:
            response = ping(ip)
            if response is not None:
                pinged = True
        
        print(f"MTConnect agent at {ip} is active")
    
    def get_data(self):
        raw_data = self.__request_agent('current')
        self.component_ids = []

        component_stream = raw_data.MTConnectStreams.Streams.DeviceStream.ComponentStream
        if not isinstance(component_stream, omegaconf.listconfig.ListConfig):
            component_stream = [component_stream]
        
        for component_data in component_stream:
            component_id = component_data['@componentId']
            self.component_ids.append(component_id)
            self.attributes[component_id] = {}
            self.data[component_id] = {}
            
            for key in component_data.keys():
                # Everything except Events and Samples are attributes
                if key not in ['Events', 'Samples']:
                    self.attributes[component_id][key] = component_data[key]
                # Events and Samples are data items
                else:
                    for data_item_list in component_data[key].values():
                        if not isinstance(data_item_list, omegaconf.listconfig.ListConfig):
                            data_item_list = [data_item_list]                            
                        for data_item in data_item_list:
                            data_item_id = data_item['@dataItemId']
                            # self.data[component_id][data_item_id] = {}
                            for key in data_item.keys():
                                data_item_key = data_item_id + '/' + key
                                self.data[component_id][data_item_key] = data_item[key]
                                # self.data[component_id][data_item_id][key] = data_item[key]
            
    def update_data(self):
        raw_data = self.__request_agent('sample')
        
        component_stream = raw_data.MTConnectStreams.Streams.DeviceStream.ComponentStream
        if not isinstance(component_stream, omegaconf.listconfig.ListConfig):
            component_stream = [component_stream]
        
        for component_data in component_stream:
            component_id = component_data['@componentId']
            
            if component_id not in self.component_ids:
                print(f"Component {component_id} not found in current data. Re-initializing data ...")
                self.get_data()
                return
            
            for key in component_data.keys():
                if key in ['Events', 'Samples']:
                    for data_item_list in component_data[key].values():
                        if not isinstance(data_item_list, omegaconf.listconfig.ListConfig):
                            data_item_list = [data_item_list]                            
                        for data_item in data_item_list:
                            data_item_id = data_item['@dataItemId']
                            # self.data[component_id][data_item_id] = {}
                            for key in data_item.keys():
                                data_item_key = data_item_id + '/' + key
                                self.data[component_id][data_item_key] = data_item[key]
                                # self.data[component_id][data_item_id][key] = data_item[key]
                                            
    def __request_agent(self, ext: str):
        URL = self.cfg['mtconnect']['agent_url']
        response = requests.get(URL + ext)
        val = xmltodict.parse(response.text, encoding='utf-8')
        val = OmegaConf.create(val)        
        return val
