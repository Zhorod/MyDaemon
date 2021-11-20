import paho.mqtt.client as mqtt #import the client1
#broker_address="127.0.0.1"
broker_address="192.168.1.72"

#broker_address="iot.eclipse.org" #use external broker
client = mqtt.Client("P1") #create new instance
client.connect(broker_address, 1883) #connect to broker
client.publish("mydaemon","OFF")#publish