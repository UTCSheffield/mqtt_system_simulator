
from mqtt_device import MQTTClient, FishTankDevice
import time

# Example: Front end can register multiple devices and interact with them
mqttc = MQTTClient()
mqttc.set_local(True)

# Register one or more devices (example with TankDevice)
tank_device = FishTankDevice()
mqttc.register_device(tank_device)

# Start the MQTT client
mqttc.run()

# Main loop: update and publish data for all registered devices
while True:
	mqttc.update_data()
	mqttc.publish_data()
	time.sleep(10)
