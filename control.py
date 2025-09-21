from mqtt_device import MQTTClientNull, MQTTClientLocal, MQTTClient, FishTankController, add_method
import time

# Create the MQTT client with a FishTankController
mqttc = MQTTClient(FishTankController())

# Task 1a : Implement heater control logic
@add_method(FishTankController)
def heater_control(temperature: float):
    turn_heater_on = False
    
    print("Heater control checking temperature:", temperature, "C   ->", turn_heater_on)
    return turn_heater_on 

#assert heater_control(50.0) == False, "Heater should be off at 50.0C"
#assert heater_control(0.0) == True, "Heater should be on at 0.0C"
'''
# Task 1b : Implement light control logic
@add_method(FishTankController) 
def light_control(lux: float, hour: int):
    turn_light_on = False
    
    #print("Light control checking lux:", lux, "hour:", hour, "->", turn_light_on)
    return turn_light_on

#assert light_control(1000.0, 12) == False, "Light should be off at 1000 lux"
#assert light_control(50.0, 12) == True, "Light should be on at 50 lux"

# Task 1c : Implement pump control logic
@add_method(FishTankController)     
def pump_control(pH: float, hour: int):
    turn_pump_on = False

    #print("Pump control checking pH:", pH, "hour:", hour, "->", turn_pump_on)
    return turn_pump_on

#assert pump_control(7.0, 12) == False, "Pump should be off at pH 7.0"
#assert pump_control(2.0, 12) == True, "Pump should be on at pH 6.0"
'''

# Task 2 : Implement data logging and display
'''
Process the incoming data into a useable format
The data comes in 2 different formats just text (JSON) and separate parameters
Produce a live Print out / Representation / Dashboard (pick the tech you can manage)
'''
@add_method(FishTankController)
def on_new_data(temperature: float, pH: float, lux: float, hour: int):
    log_entry = f"Data Received - Time: {hour}:00, Temperature: {temperature} C, pH: {pH}, Light: {lux} lux"
    print(log_entry)
    return log_entry

@add_method(FishTankController)
def on_new_data_str(data_str: str):
    print("Data String Received:", data_str)
    return data_str

#Task 3 : Data storage and analysis
'''
Store the incoming data  in a CSV file?
'''

# Task 4 : Data visualisation
'''
Output formatted data from the CSV file, e.g. temperature over time.
 Tables
 Averages
 Graphs
'''



# Main loop: update and publish data for all registered devices
while True:
    mqttc.update_data()
    mqttc.publish_data()
    time.sleep(10)

