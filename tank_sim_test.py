from mqtt_device import TankSimulator
import time

# Create a TankSimulator instance
tank_sim = TankSimulator()
tank_sim.set_local(True)  # Use local broker for development

# Start the MQTT client loop
tank_sim.run()

# Main loop: update and publish data
while True:
    tank_sim.update_data(10)  # Pass time delta (e.g., 10 seconds)
    for topic, payload, qos, retain in tank_sim.get_publish_payloads():
        tank_sim.publish(topic, payload=payload, qos=qos, retain=retain)
    time.sleep(10)


    