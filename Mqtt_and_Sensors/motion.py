import paho.mqtt.client as PahoMQTT
import datetime
import json
import time
from gpiozero import MotionSensor
import requests


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
        self._paho_mqtt = PahoMQTT.Client(self.clientID, True)
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

    FILENAME = "config_sensors.json"
    with open(FILENAME, "r") as f:
        d = json.load(f)
        IP_RASP = d["servicecat_ip"]
        house_id = d["house_id"]
        room_id = d["room_id"]
        motion_id = d["motion_id"]
        mqtt_interval = d["mqtt_interval"]

    RESOURCE = "../Catalog/configuration.json"
    with open(RESOURCE, "r") as f:
        d = json.load(f)
        CATALOG_NAME = d["catalog_list"][1]["resource_id"]

    # Mqtt broker parameters
    from_config = IP_RASP
    broker = requests.get(from_config + "get_broker").json()
    port = requests.get(from_config + "get_broker_port").json()

    # Resource
    resource_ip = requests.get(from_config + "get_address?id=" + CATALOG_NAME).json()
    resource_cat = resource_ip["ip"] + ":" + str(resource_ip["port"])
    topic = requests.get("http://" + resource_cat + "/get_topic?id=" + house_id + "_" + room_id + "_motion").json()
    interval_motion = requests.get("http://" + resource_cat + "/get_threshold?" + motion_id).json()

    pub = MyPublisher("Motion", broker, port)
    pub.start()
    pir = MotionSensor(18, queue_len=30, sample_rate=1)
    while True:
        status_motion = requests.get("http://" + resource_cat + "/get_status?id=" + motion_id).json()
        if status_motion["status"] == "ON":
            pub.myPublish(topic, json.dumps({"DeviceID": house_id + "_" + room_id + "_motion", "value": pir.value}))
            print("publishing value of pir : ", pir.value)
        else:
            print("Motion OFF")
        time.sleep(mqtt_interval)

    time_pub.stop()


