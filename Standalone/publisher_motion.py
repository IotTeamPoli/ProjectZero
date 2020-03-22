import paho.mqtt.client as PahoMQTT
import datetime
import json
import time
from gpiozero import MotionSensor


class MyPublisher:

    def __init__(self, clientID, broker="192.168.1.254", port=1884):
        self.clientID = clientID
        self.port = port
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        self._paho_mqtt.on_connect = self.myOnConnect
        self.messageBroker = broker

    def start(self):
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))


if __name__ == "__main__":
    broker = "192.168.1.254"
    porta = 1884

    time_pub = MyPublisher("Motion", broker, porta)
    time_pub.start()
    pir = MotionSensor(18)

    while True:
        pir.wait_for_motion()

        dmytime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        dmytimej = json.dumps({'current time in dd-mm-yyyy hh:mm format': dmytime})
        print("Publishing:'%s'" % dmytime)
        time_pub.myPublish('/dmytime', dmytimej)
        time_pub.myPublish('/motion', "motion detected")
        print("motion detected ")
        pir.wait_for_no_motion()
        print("not anymore")
    time_pub.stop()
