import paho.mqtt.client as PahoMQTT
import requests
import json
import time

# Global configuration variables
config_file = '../Catalog/configuration.json'
config = open(config_file, 'r')
configuration = config.read()
config.close()
config = json.loads(configuration)
service_address = config['servicecat_address']
resource_id = config["catalog_list"][1]["resource_id"]
presence_id = config["catalog_list"][2]["presence_id"]

res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"

ip_presence = requests.get(service_address + "get_address?id=" + presence_id).json()
from_config = "http://" + ip_presence["ip"] + ":" + str(ip_presence["port"])
uri_get_whitelist = from_config + "/print_all_whitelist"
uri_get_blacklist = from_config + "/print_all_blacklist"
uri_get_unknownlist = from_config + "/print_all_unknown"
uri_add_unknown = from_config + "/add_to_unknown"
uri_add_white = from_config + "/add_to_white"
uri_add_black = from_config + "/add_to_black"
uri_inside = from_config + "/get_all_inside"  # return list
uri_all = from_config + "/get_all_records"
uri_rmv = from_config + "/rmv_this_person"
turn_presence = from_config + "/turn_presence"


def register_unknown(house_id, mac, device, add_to_unknown):
    name = "unknown"
    surname = "unknown"
    now = time.time()
    # format
    param = {"home": house_id,
             "mac": mac,
             "name": name,
             "surname": surname,
             "device_name": device,
             "present": True,
             "last_detected": now}
    response = requests.put(add_to_unknown, param)
    print("registering unknown")
    return response


class MyMQTT:
    def __init__(self, clientID, broker, port, topic):
        self.broker = broker
        self.port = port
        self.clientID = clientID

        self._topic = topic
        self._isSubscriber = False

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, True)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect(self, paho_mqtt, userdata, flags, rc):
        print("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived(self, paho_mqtt, userdata, msg):
        # A new message is received
        print("received '%s' under topic '%s'" % (msg.payload, msg.topic))
        # The message we expect has the format: {"Device_ID": "house_room_device_list", "value": "mac","device_name":""}
        message_obj = json.loads(msg.payload)
        items = message_obj["DeviceID"].split("_")
        house = items[0]
        value = message_obj["value"]
        device_name = message_obj["device_name"]
        records = requests.get(uri_all).json()
        flag = 0
        for i in records:
            if i["mac"] == value:
                print("present")
                requests.put(turn_presence, {"home": house, "mac": value})
                flag = 1
        if flag == 0:
            try:
                register_unknown(house, value, device_name, uri_add_unknown)
            except Exception as e:
                print(" http error: ", e)

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


if __name__ == '__main__':
    brokermqtt = requests.get(service_address + "get_broker").json()
    portmqtt = requests.get(service_address + "get_broker_port").json()

    topicmqtt = requests.get(resource_address + "get_topic?id=" + resource_id).json().split("/")
    print(topicmqtt)
    topicmqtt[2] = "+"
    topicmqtt = "/".join(topicmqtt)
    topicmqtt = topicmqtt + "/+/bluetooth"
    # ioteam/resourcecat/+/+/bluetooth

    presenceStrategy = MyMQTT("PresenceStrategy", brokermqtt, portmqtt, topicmqtt)
    presenceStrategy.start()
    presenceStrategy.mySubscribe(topicmqtt)  # All the topic you can have through requests

    while True:
        time.sleep(5)
    presenceStrategy.stop()
