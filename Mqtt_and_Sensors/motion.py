import paho.mqtt.client as PahoMQTT
import datetime
import json
import time
from gpiozero import MotionSensor
import requests

FILENAME = "config_sensors.json"


class MyPublisher:
    """
    default broker and port are provided
    create publisher:
    pub = MyPublisher("ID of pub", broker, port)
    pub.start()
    pub.myPublish("topic",values)
    pub.stop()
    """

    def __init__(self, clientID, broker="192.168.1.254", port=1884):
        self.clientID = clientID
        self.port = port
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self.messageBroker = broker
        # self.messageBroker = 'iot.eclipse.org'

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.messageBroker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish(self, topic, message):
        # publish a message with a certain topic qos 2
        self._paho_mqtt.publish(topic, message, 2)

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))


if __name__ == "__main__":

    with open(FILENAME, "r") as f:
        d = json.load(f)
        PORT = d["service_cat_port"]
        IP_RASP = d["service_cat_ip"]
        house_id = d["house_id"]
        camera_id = d["camera_id"]

    # Service Cat RETRIVE
    from_config = IP_RASP + ":" + PORT
    broker = requests.get("http://" + from_config + "/get_broker").json()
    port = requests.get("http://" + from_config + "/get_broker_port").json()
    resource_ip = requests.get("http://" + from_config + "/get_ip?id=ResourceCatalogue").json()
    resource_port = requests.get("http://" + from_config + "/get_port?id=ResourceCatalogue").json()

    # Resource
    resource_cat = resource_ip + ":" + resource_port
    topic = requests.get("http://" + resource_cat + "/get_topic?id=" + house_id + "_" + camera_id).json()

    pub = MyPublisher("Motion", broker, port)
    pub.start()
    pir = MotionSensor(18, queue_len=30, sample_rate=1)
    while True:
        pub.myPublish(topic, json.dumps({"DeviceID": house_id + "_" + camera_id + "_motion", "value": pir.value}))
        print("value of pir :  ")
        print(pir.value)
        time.sleep(30)

    time_pub.stop()

# TODO make better code and be more Object Oriented
