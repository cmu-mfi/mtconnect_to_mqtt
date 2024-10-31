#!/usr/bin/env python3

from core.mtconnect import MTConnect

if __name__ == "__main__": 
    
    data_obj = MTConnect()
    
    data_obj.get_data()
    print(data_obj.component_ids)
    input("Press Enter to continue...")
    print(data_obj.data)
    
    breakpoint()
    data_obj.update_data()
    
    breakpoint()
    print(data_obj.data)