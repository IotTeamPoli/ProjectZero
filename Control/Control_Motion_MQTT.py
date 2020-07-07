# request get insieme all'alert

# !/usr/bin/python
# -*- coding: utf-8 -*-

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
resource_id = config["catalog_list"][1]["resource_id"]
res_address = requests.get(service_address + "get_address?id=" + resource_id).json()
resource_address = "http://" + res_address["ip"] + ":" + str(res_address["port"]) + "/"


# indirizzo della camera


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
        # The message we expect has the format: {"Device_ID": "house_room_device", "value":value}
        message_obj = json.loads(msg.payload)
        device_id = message_obj["DeviceID"]
        items = message_obj["DeviceID"].split("_")
        value = float(message_obj["value"])
        device = items[2]
        house = items[0]
        room = items[1]
        if device == "motion":
            threshold = requests.get(resource_address + "get_threshold?device_id=" + device_id).json()
            print(threshold)

            if value > threshold["threshold"]:

                pub_topic = requests.get(resource_address + "get_topic_alert?house=" + house + "&device=motion").json()[
                    "topic"]
                print(pub_topic)
                msg = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS MOVEMENT VALUE HAS BEEN DETECTED IN ROOM " + room + "!!!"
                answer = {"motion_strategy": msg}
                answer["room"] = room
                print(answer)
                # dalla resource
                camera_ad = requests.get(service_address + "get_address?id=" + house + "_" + room + "_camera").json()
                camera_address = "http://" + camera_ad["ip"] + ":" + str(camera_ad["port"]) + "/"
                print(camera_address + "take_picture")
                # http://192.168.1.178:8082/take_picture
                photo = requests.get(camera_address + "take_picture").json()
                if photo['msg'] != 'an error occured in camera server':  # exception in camera_server
                    answer["photo"] = photo['msg']  # --> controlla formato per il re-inoltro
                else:
                    answer['photo'] = ''
                self.myPublish(pub_topic, json.dumps(answer))
                # print("publishing on topic: ", pub_topic)

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
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()


if __name__ == "__main__":
    broker = requests.get(service_address + "get_broker").json()
    port = requests.get(service_address + "get_broker_port").json()
    topic = requests.get(resource_address + "get_topic?id=" + resource_id).json().split("/")
    # iotteam/resourcecat/#
    print("topic :", topic)
    topic[2] = "+"
    topic = "/".join(topic)
    topic = topic + "/+/motion"

    motionStrategy = MyMQTT("motionStrategy", broker, port, topic)
    motionStrategy.start()
    motionStrategy.mySubscribe(topic)  # All the topic you can have through requests

    while True:
        time.sleep(5)

    motionStrategy.stop()
