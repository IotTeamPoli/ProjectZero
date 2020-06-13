import paho.mqtt.client as PahoMQTT
import requests
import json
import ast
import time

# Global configuration variables
config_file = '../Catalog/configuration.json'
config = open(config_file, 'r')
configuration = config.read()
config.close()
config = json.loads(configuration)
service_address = config['servicecat_address']
presence_id = config["catalog_list"][2]["presence_id"]
res_address = requests.get(service_address + "get_address?id=" + presence_id).json()
resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"


class MyMQTT:
    def __init__(self, clientID, broker, port, topic):
        self.broker = broker
        self.port = port
        self.clientID = clientID

        self._topic = topic
        self._isSubscriber = False

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        print("received '%s' under topic '%s'" % (msg.payload, msg.topic))
        # The message we expect has the format: {"Device_ID": "house_room_device_list", "value": "mac"}
        message_obj = json.loads(msg.payload)
        device_id = message_obj["DeviceID"]
        items = message_obj["DeviceID"].split("_")
        value = json.loads(message_obj["value"])
        device = items[2]
        house = items[0]
        room = items[1]
        list = items[3]
        print(device == "bluetooth")
        from_config = connection(service_address, presence_id)
        # methods
        uri_get_whitelist = from_config + "/print_all_whitelist"
        uri_get_blacklist = from_config + "/print_all_blacklist"
        uri_get_unknownlist = from_config + "/print_all_unknown"
        uri_add_unknown = from_config + "/add_to_unknown"
        uri_add_white = from_config + "/add_to_white"
        uri_add_black = from_config + "/add_to_black"
        rmv = from_config + "/rmv_this_person"


    def mySubscribe(self, topic):
        # if needed, you can do some computation or error-check before subscribing
        print("subscribing to %s" % (topic))
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic

    def myPublish(self, topic, msg):
        # self._isSubscriber = False
        print("publishing '%s' with topic '%s'" % (msg, topic))
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, msg, 2)

    def start(self):
        # manage connection to broker
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        if self._isSubscriber:
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


def connection(ip, cat_name):
    ip_presence = requests.get(ip + "get_address?id=" + cat_name).json()
    return "http://" + ip_presence["ip"] + ":" + str(ip_presence["port"])


def list_search(get_uri, add_uri, rmv, mac_lists):
    present = []
    response = requests.get(get_uri)
    for j in response.json():
        present.append(j["mac"])
        if j["mac"] in mac_lists:  # detected or not
            print("person detected")
            requests.put(rmv, j)
            j["present"] = "present"
            requests.put(add_uri, j)
        else:
            requests.put(rmv, j)
            j["present"] = "not_present"
            requests.put(add_uri, j)
    return present



if __name__ == '__main__':

    broker = requests.get(service_address + "get_broker").json()
    port = requests.get(service_address + "get_broker_port").json()

    topic = requests.get(resource_address + "get_topic?id=" + presence_id).json().split("/")
    # iotteam/resourcecat/#
    print("topic :", topic)
    topic[2] = "+"
    topic = "/".join(topic)
    topic = topic + "/+/bluetooth"


    presenceStrategy = MyMQTT("PresenceStrategy", broker, port, topic)
    presenceStrategy.start()
    presenceStrategy.mySubscribe(topic)  # All the topic you can have through requests

    while True:
        time.sleep(5)
    motionStrategy.stop()
