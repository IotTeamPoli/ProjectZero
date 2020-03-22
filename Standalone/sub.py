import requests
import time
import json
import paho.mqtt.client as PahoMQTT


class MySubscriber:
    def __init__(self, clientID, broker="192.168.1.254", port=1884, topic="/mytopic"):
        self.clientID = clientID
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
        self.topic = topic
        self.messageBroker = broker
        self.port = port

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()
        self._paho_mqtt.subscribe(self.topic, 2)

    def stop(self):
        self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        print("Topic: '" + msg.topic + "', Qos: '" + str(msg.qos) + "' Message: '" + str(msg.payload) + "'")


if __name__ == '__main__':
    broker_ip = "192.168.5.35"
    mqtt_port = 1884

    time_sub = MySubscriber("time", broker_ip, mqtt_port, '/dmytime')
    hum_sub = MySubscriber("hum", broker_ip, mqtt_port, '/hum')
    temp_sub = MySubscriber("temp", broker_ip, mqtt_port, '/temp')
    motion_sub = MySubscriber("motion", broker_ip, mqtt_port, '/motion')
    hum_sub.start()
    temp_sub.start()
    time_sub.start()
    motion_sub.start()
    while True:
        time.sleep(1)

    time_sub.stop()
    hum_sub.stop()
    temp_sub.stop()
    motion_sub.stop()
