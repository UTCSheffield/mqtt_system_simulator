from mqtt_device import MQTTClient, FishTankDevice
import time

# Example: Display subscribes to device data and prints it
class DisplayDevice(FishTankDevice):
	def on_message(self, mqttc, obj, msg):
		print(f"Display received: {msg.topic} {msg.payload}")

# Create the MQTT client
mqttc = MQTTClient()
mqttc.set_local(True)

# Create and register display device
display_device = DisplayDevice()
mqttc.register_device(display_device)

# Start the MQTT client
mqttc.run()

# Main loop: just keep the client running
while True:
	time.sleep(10)
