import paho.mqtt.client as PahoMQTT
import requests
import json
import time

# Global configuration variables
config_file = '../Catalog/configuration.json'
config = open(config_file, 'r')
configuration = config.read()
config.close()
try:
    config = json.loads(configuration)
    service_address = config['servicecat_address']
    resource_id = config["catalog_list"][1]["resource_id"]
    res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
    resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"
except Exception as e:
    print("Some catalogs might not be active yet: " + str(e))

class MyMQTT:
    def __init__(self, clientID, broker, port, topic):
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self._topic = topic

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, True)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        try:
            print("received '%s' under topic '%s'" % (msg.payload, msg.topic))
            # The message we expect has the format: {"DeviceID": "house_room_device", "value":value}
            message_obj = json.loads(msg.payload)
            device_id = message_obj["DeviceID"]
            value = message_obj["value"]
            items = device_id.split("_")
            house = items[0]
            device = items[2]
            if device == "gas":
                threshold = requests.get(resource_address + "get_threshold?device_id=" + device_id).json()
                if value > threshold["threshold"]:
                    pub_topic = requests.get(resource_address + "get_topic_alert?house=" + house + "&device=gas").json()["topic"]
                    msg = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS GAS VALUE HAS BEEN DETECTED!!! CHECK IF YOU TURNED" \
                    " OFF THE GAS!!!"
                    answer = {"gas_strategy": msg}
                    self.myPublish(pub_topic, json.dumps(answer))
        except Exception as e:
            print("error: ", str(e))

    def mySubscribe(self, topic):
        # if needed, you can do some computation or error-check before subscribing
        print("subscribing to %s" % (topic))
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._topic = topic

    def myPublish(self, topic, msg):
        print("publishing '%s' with topic '%s'" % (msg, topic))
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, msg, 2)
        print("publishing '%s' with topic '%s'" % (msg, topic))

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        # remember to unsuscribe if it is working also as subscriber
        self._paho_mqtt.unsubscribe(self._topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


if __name__ == "__main__":
    try:
        broker = requests.get(service_address + "get_broker").json()
        port = requests.get(service_address + "get_broker_port").json()
        if port == -1:
            raise Exception("Broker port not found.")
        topic = requests.get(resource_address + "get_topic?id=" + resource_id).json().split("/")
        if topic[0].startswith("Error"):
            raise Exception("Topic not found.")
        topic[2] = "+"
        topic = "/".join(topic)
        topic = topic + "/+/gas"  # ioteam/resourcecat/+/+/gas

        gasStrategy = MyMQTT("gasStrategy", broker, port, topic)
        gasStrategy.start()
        gasStrategy.mySubscribe(topic)  # All the topic you can have through requests

        while True:
            time.sleep(5)

        gasStrategy.stop()
    except Exception as e:
        print("The gas control strategy cannot start yet. Exception: " + str(e))
