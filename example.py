import time
from mqtt_device import MQTTClient, TankSimulator

# Create the MQTT client
mqttc = MQTTClient()
mqttc.set_local(True)  # Use local broker for development

# Create a tank simulator device
tank_sim = TankSimulator()

# Register the tank simulator with the MQTT client
mqttc.register_device(tank_sim)

# Start the MQTT client
mqttc.run()

# Main loop: update and publish data for all registered devices
while True:
    mqttc.update_data()
    mqttc.publish_data()
    time.sleep(10)