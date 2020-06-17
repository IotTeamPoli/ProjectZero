import bluetooth
import requests
import time
import json
import paho.mqtt.client as PahoMQTT

FILENAME = "config_sensors.json"
with open(FILENAME, "r") as f:
    d = json.load(f)
    IP_RASP = d["servicecat_ip"]
    house_id = d["house_id"]

RESOURCE = "../Catalog/configuration.json"
with open(RESOURCE, "r") as f:
    d = json.load(f)
    CATALOG_NAME = d["catalog_list"][1]["resource_id"]


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



def connection(ip, cat_name):
    ip_presence = requests.get(ip + "get_address?id=" + cat_name).json()
    return "http://" + ip_presence["ip"] + ":" + str(ip_presence["port"])



def main():
    from_config = IP_RASP
    broker = requests.get(from_config + "get_broker").json()

    port_broker = requests.get(from_config + "get_broker_port").json()
    port = port_broker

    resource_ip = requests.get(from_config + "get_address?id=" + CATALOG_NAME).json()
    print(from_config + "get_address?id=" + CATALOG_NAME)

    # Resource
    resource_cat = resource_ip["ip"] + ":" + str(resource_ip["port"])
    topic_presence = requests.get("http://" + resource_cat + "/get_topic?id=house1_Kitchen_bluetooth").json()
    print("http://" + resource_cat + "/get_topic?id=house1_Kitchen_bluetooth")
    print(topic_presence)
    presence_pub = MyPublisher("presence", broker, port)

    while True:
        # scanning all present devices and create a list of present macs
        print("performing inquiry...")
        nearby_devices = bluetooth.discover_devices(duration=10, lookup_names=True, flush_cache=True,
                                                    lookup_class=False)
        print("found %d devices" % len(nearby_devices))
        # iterating
        for mac, device_name in nearby_devices:
            try:
                print("\t%s - %s" % (mac, device_name))
                presence_pub.myPublish(topic_presence,
                                       json.dumps({"DeviceID": "house1_Kitchen_bluetooth", "value": mac}))
            except Exception as e:
                print('error : ', e)
        time.sleep(50)


if __name__ == '__main__':
    main()
