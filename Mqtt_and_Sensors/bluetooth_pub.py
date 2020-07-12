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
    bluetooth_id = d["bluetooth_id"]
    mqtt_interval = d["mqtt_interval"]

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

    def __init__(self, clientID, broker="192.168.1.254", port=1883):
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
        print("publishing '%s' with topic '%s'" % (message, topic))

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))


def main():
    from_config = IP_RASP
    broker = requests.get(from_config + "get_broker").json()
    port = requests.get(from_config + "get_broker_port").json()

    resource_ip = requests.get(from_config + "get_address?id=" + CATALOG_NAME).json()

    # Resource
    resource_cat = resource_ip["ip"] + ":" + str(resource_ip["port"])
    topic_presence = requests.get("http://" + resource_cat + "/get_topic?id=house1_Kitchen_bluetooth").json()
    presence_pub = MyPublisher("PresencePUB", broker, port)
    presence_pub.start()

    while True:
        # scanning all present devices and create a list of present macs
        try:
            status = requests.get("http://" + resource_cat + "/get_status?" + bluetooth_id).json()
            print(status)
            if status["status"] == "ON":
                print("performing inquiry...")
                nearby_devices = bluetooth.discover_devices(duration=10, lookup_names=True, flush_cache=True,
                                                            lookup_class=False)
                print("found %d devices" % len(nearby_devices))
                # iterating
                if len(nearby_devices) == 0:
                    presence_pub.myPublish(topic_presence,
                                           json.dumps(
                                               {"DeviceID": bluetooth_id, "value": "FF:FF:FF:FF:FF:FF",
                                                "device_name": "dummy_device"}))
                for mac, device_name in nearby_devices:
                    try:
                        print("\t%s - %s" % (mac, device_name))
                        presence_pub.myPublish(topic_presence,
                                               json.dumps({"DeviceID": bluetooth_id, "value": mac,
                                                           "device_name": device_name}))
                    except Exception as e:
                        print('error : ', e)
            else:
                print("bluetooth OFF")
        except Exception as e:
            print('error : ', e)
        time.sleep(mqtt_interval)


if __name__ == '__main__':
    main()
