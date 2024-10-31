import os
import requests
import xmltodict
from omegaconf import OmegaConf

URL = 'http://192.168.1.100:8082/'

def get_current():
    response = requests.get(URL + 'current')
    return parse_xml(response.text)

def get_probe():
    response = requests.get(URL + 'probe')
    return parse_xml(response.text)

def get_sample():
    response = requests.get(URL + 'sample')
    return parse_xml(response.text)

def parse_xml(xml): 
    val = xmltodict.parse(xml, encoding='utf-8')
    val = OmegaConf.create(val)
    return val
    
    
if __name__ == '__main__':      
    
    print("Choose an option for data:")
    print("1. Current")
    print("2. Probe")
    print("3. Sample")
        
    data_choice = input('Enter your choice (1/2/3): ')
    data = None
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = None
    
    match data_choice:
        case '1':
            data = get_current()
            file_path = os.path.join(script_dir, 'current.yaml')
        case '2':
            data = get_probe()
            file_path = os.path.join(script_dir, 'probe.yaml')
        case '3':
            data = get_sample()
            file_path = os.path.join(script_dir, 'sample.yaml')
        case _:
            print("Invalid choice")
            exit()
    
    with open(file_path, 'w') as f:
        f.write(OmegaConf.to_yaml(data))
    
    print("Data saved to ", file_path)
    
    # print(get_probe())