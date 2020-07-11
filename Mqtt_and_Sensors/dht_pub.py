import datetime
import json
import time
import Adafruit_DHT
import paho.mqtt.client as PahoMQTT
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

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.messageBroker, rc))


if __name__ == "__main__":
    FILENAME = "config_sensors.json"
    with open(FILENAME, "r") as f:
        d = json.load(f)
        IP_RASP = d["servicecat_ip"]
        house_id = d["house_id"]
        temp_id = d["temp_id"]
        hum_id = d["hum_id"]
        mqtt_interval = d["mqtt_interval"]

    RESOURCE = "../Catalog/configuration.json"
    with open(RESOURCE, "r") as f:
        d = json.load(f)
        CATALOG_NAME = d["catalog_list"][1]["resource_id"]

    # Mqtt broker parameters
    from_config = IP_RASP
    broker = requests.get(from_config + "get_broker").json()
    port = requests.get(from_config + "get_broker_port").json()

    # Resource catalogue setup
    resource_ip = requests.get(from_config + "get_address?id=" + CATALOG_NAME).json()
    resource_cat = resource_ip["ip"] + ":" + str(resource_ip["port"])
    topic_temp = requests.get("http://" + resource_cat + "/get_topic?id=house1_Kitchen_temperature").json()
    topic_humi = requests.get("http://" + resource_cat + "/get_topic?id=house1_Kitchen_humidity").json()

    DHT_TYPE = Adafruit_DHT.DHT11
    DHT_PIN = 4

    temp_hum = MyPublisher("temp_hum", broker, port)
    temp_hum.start()

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
        if humidity is not None and temperature is not None:
            print('Temp={0:0.1f}*C Humidity={1:0.1f}%'.format(temperature, humidity))
        else:
            print('failed reading\n')
        print("Publishing temperature and humidity")
        status_temp = requests.get("http://" + resource_cat + "/get_status?" + temp_id).json()
        if status_temp["status"] == "ON":
            temp_hum.myPublish(topic_temp, json.dumps({"DeviceID": "house1_Kitchen_temperature", "value": temperature}))
            print("publishing temperature")
            time.sleep(mqtt_interval)
        else:
            print("temperature OFF")
        status_hum = requests.get("http://" + resource_cat + "/get_status?" + hum_id).json()
        if status_hum["status"] == "ON":
            temp_hum.myPublish(topic_humi, json.dumps({"DeviceID": "house1_Kitchen_humidity", "value": humidity}))
            print("publishing humidity")
            time.sleep(mqtt_interval)
        else:
            print("humidity OFF")
            time.sleep(mqtt_interval)
    temp_hum.stop()
