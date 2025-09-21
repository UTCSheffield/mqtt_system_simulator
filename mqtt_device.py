
#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution.
#
# The Eclipse Distribution License is available at
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation

# This example shows how you can use the MQTT client in a class.

#import context  # Ensures paho is in PYTHONPATH

import paho.mqtt.client as mqtt
#from dataclasses import dataclass
from timeit import default_timer as timer
import time
import json
from functools import wraps # This convenience func preserves name and docstring
import os
import sys

def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(*args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator


#@dataclass
class MQTTClientNull(mqtt.Client):
    debug = False
    individual_publish = False
    devices = None

    def __init__(self, register=[], **kwargs):
        if not isinstance(register, list):
            register = [register]
        
        self.client_id = os.getlogin()+"-"+os.path.basename(sys.argv[0]).replace(".py","")
        print("Client ID:", self.client_id)
        super(MQTTClientNull, self).__init__(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
            protocol=mqtt.MQTTv5,
            **kwargs)
        
        self.devices = []
        if len(register) > 0:
            for device in register:
                self.register_device(device)


    def register_device(self, device):
        self.devices.append(device)
        
    def on_connect(self, mqttc, obj, flags, reason_code, properties):
        if self.debug:
            print("Connected rc: "+str(reason_code))

    def on_connect_fail(self, mqttc, obj):
        if self.debug:
            print("Connect failed")

    def on_message(self, mqttc, obj, msg):
        if self.debug:
            print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        # Route message to correct device
        for device in self.devices:
            if hasattr(device, "on_message"):
                device.on_message(mqttc, obj, msg)
    
    def update_data(self):
        for device in self.devices:
            if hasattr(device, "update_data"):
                device.update_data()

    def publish_data(self):
        for device in self.devices:
            if hasattr(device, "get_publish_payloads"):
                for topic, payload, qos, retain in device.get_publish_payloads():
                    self.publish(topic, payload=payload, qos=qos, retain=retain)
    
    def update_hardware(self):
        pass
        
    def on_publish(self, mqttc, obj, mid, reason_codes, properties):
        if self.debug:
            print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, reason_code_list, properties):
        if self.debug:
            print("Subscribed: "+str(mid)+" "+str(reason_code_list))

    def on_log(self, mqttc, obj, level, string):
        if self.debug:
            print(string)
    
    def run(self):
        pass

class MQTTClient(MQTTClientNull):
    def __init__(self, *args, **kwargs):
        super(MQTTClient, self).__init__(*args, **kwargs)
        self.run()
        
    def run(self):
        self.connect("4f8d5d75e7ee4747a9c3043262312926.s1.eu.hivemq.cloud", 8883)
        self.subscribe("OLP/device/#", qos=1)
        
        # TODO : the controller could be launched with loop forever if the on_message calls update_data and publish_data 
        self.loop_start()

class MQTTClientLocal(MQTTClient):
    def run(self):
        self.connect("127.0.0.1")  # use port 1883 for unencrypted connection
        self.subscribe("OLP/device/#", qos=1)
        
        # TODO : the controller could be launched with loop forever if the on_message calls update_data and publish_data 
        self.loop_start()


# Base class for all device types
class DeviceBase:
    dirty = False
    individual_publish = False
    time_multiplier = 1.0
    simulate = False
    #last_time = None

    
    def __init__(self, *args, **kwargs):
        if "on_new_data_str" in kwargs:
            # stash this function for use on heater update
            self.on_new_data_str = kwargs["on_new_data_str"]
        if "on_new_data" in kwargs:
            # stash this function for use on heater update
            self.on_new_data = kwargs["on_new_data"]
        
        
    def on_message(self, mqttc, obj, msg):
        print("on_message: "+msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        pass

    def update_simulation(self):
        pass
    
    def update_data(self):
        now_time = timer()
        self.diff = int(now_time - getattr(self, 'last_time', now_time))
        setattr(self, 'last_time', now_time)
        self.update_simulation()
        
    def update_hardware(self):
        pass    
    
    def get_publish_payloads(self):
        return []

    def do_on_new_data(self):
        self.on_new_data_str(json.dumps({
            'temperature': round(self.temperature, 2),
            'lux': round(self.lux, 2),
            'humidity': round(self.humidity, 2),
            'ambient_temperature': round(self.ambient_temperature, 2)
            }))
        
        self.on_new_data(
            temperature = round(self.temperature, 2),
            lux = round(self.lux, 2),
            humidity = round(self.humidity, 2),
            ambient_temperature = round(self.ambient_temperature, 2)
        )

    def on_new_data_str(self, data: str):
        pass

    def on_new_data(self, temperature: float, lux: float, humidity: float, ambient_temperature: float):
        pass
        

class FishTankDevice(DeviceBase):
    temperature: float = 15.0
    ambient_temperature: float = 10.0
    lux: float = 1.85
    humidity: float = 1.85
    
    heater: bool = False
    light: bool = False
    pump: bool = False
    
    def __repr__(self):
        return self.__class__.__name__ + f'(temperature={self.temperature}, lux={self.lux}, humidity={self.humidity}, heater={self.heater}, light={self.light}, pump={self.pump})'

    def update_data(self):
        super(FishTankDevice, self).update_data()
    
    def update_simulation(self):
        temp_change = (self.ambient_temperature - self.temperature) * 0.01 * self.diff * self.time_multiplier
        if self.heater:
            temp_change = 0.1 * self.diff * self.time_multiplier
        
        self.temperature = round(self.temperature + temp_change, 2)
        self.humidity += round((0.1 * self.diff * self.time_multiplier) if self.pump else (-0.1 * self.diff * self.time_multiplier), 2)
        self.dirty = True
        self.lux = round(1.85 if self.light else 0.05, 2)

        self.do_on_new_data()
    
    '''
    def update_hardware(self):
        super(TankDevice, self).update_hardware()
    '''

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        topic_parts = msg.topic.split('/')
        if topic_parts[4] == 'control':
            if self.individual_publish:
                if topic_parts[5] == 'heater':
                    self.heater = msg.payload.lower() == b'true'
                elif topic_parts[5] == 'light':
                    self.light = msg.payload.lower() == b'true'
                elif topic_parts[5] == 'pump':
                    self.pump = msg.payload.lower() == b'true'
            if topic_parts[5] == 'all':
                payload = json.loads(msg.payload)
                if 'heater' in payload:
                    self.heater = payload['heater']
                if 'light' in payload:
                    self.light = payload['light']
                if 'pump' in payload:
                    self.pump = payload['pump']
        if topic_parts[4] == 'sensors':
            if self.individual_publish:
                if topic_parts[5] == 'temperature':
                    self.temperature = float(msg.payload)
                elif topic_parts[5] == 'ambient_temperature':
                    self.ambient_temperature = float(msg.payload)
                elif topic_parts[5] == 'lux':
                    self.lux = float(msg.payload)
                elif topic_parts[5] == 'humidity':
                    self.humidity = float(msg.payload)

                print("Updated from ",topic_parts[5],":", self.temperature, self.ambient_temperature, self.lux, self.humidity)
  
            if topic_parts[5] == 'all':
                payload = json.loads(msg.payload)
                print("Payload:", payload)
                if 'temperature' in payload:
                    self.temperature = float(payload['temperature'])
                if 'ambient_temperature' in payload:
                    self.ambient_temperature = float(payload['ambient_temperature'])
                if 'lux' in payload:
                    self.lux = float(payload['lux'])          
                if 'humidity' in payload:
                    self.humidity = float(payload['humidity'])
                print("Updated from all:", self.temperature, self.ambient_temperature, self.lux, self.humidity)
            
            self.do_on_new_data()
            


    def get_publish_payloads(self):
        if not getattr(self, "dirty", True):
            return []
        self.dirty = False
        payloads = []
        if self.individual_publish:
            payloads.append(("OLP/device/tank/id/sensors/temperature", str(round(self.temperature, 2)), 1, True))
            payloads.append(("OLP/device/tank/id/sensors/lux", str(round(self.lux, 2)), 1, True))
            payloads.append(("OLP/device/tank/id/sensors/humidity", str(round(self.humidity, 2)), 1, True))
            payloads.append(("OLP/device/tank/id/sensors/ambient_temperature", str(round(self.ambient_temperature, 2)), 1, True))
        payloads.append(("OLP/device/tank/id/sensors/all", json.dumps({
            'temperature': round(self.temperature, 2),
            'lux': round(self.lux, 2),
            'humidity': round(self.humidity, 2),
            'ambient_temperature': round(self.ambient_temperature, 2)
        }), 1, True))
        return payloads
 

class FishTankController(FishTankDevice):

    def __init__(self, *args, **kwargs):
        super(FishTankController, self).__init__(*args, **kwargs)
        
        if "heater_control" in kwargs:
            # stash this function for use on heater update
            self.heater_control = kwargs["heater_control"]
        
        if "pump_control" in kwargs:
            self.pump_control = kwargs["pump_control"]
        
        if "light_control" in kwargs:
            self.light_control = kwargs["light_control"]

    def heater_control(self, temperature: float) -> bool:
        return False

    def pump_control(self, humidity: float) -> bool:
        return False    
    
    def light_control(self, lux: float) -> bool:
        return False    
    
    def update_data(self):
        super(FishTankController, self).update_data()
        heater = self.heater_control(self.temperature)
        if heater != self.heater:
            self.heater = heater
            self.dirty = True
        pump = self.pump_control(self.humidity)
        if pump != self.pump:
            self.pump = pump
            self.dirty = True
        light = self.light_control(self.lux)
        if light != self.light:
            self.light = light
            self.dirty = True

    def get_publish_payloads(self):
        if not getattr(self, "dirty", True):
            return []
        self.dirty = False
        payloads = []
        if self.individual_publish:
            payloads.append(("OLP/device/tank/id/control/heater", str(self.heater), 1, True))
            payloads.append(("OLP/device/tank/id/control/light", str(self.light), 1, True))
            payloads.append(("OLP/device/tank/id/control/pump", str(self.pump), 1, True))
        payloads.append(("OLP/device/tank/id/control/all", json.dumps({
            'heater': self.heater,
            'light': self.light,
            'pump': self.pump
        }), 1, True))
        return payloads



