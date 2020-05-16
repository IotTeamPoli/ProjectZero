#!/usr/bin/python
# -*- coding: utf-8 -*-

import paho.mqtt.client as PahoMQTT
import requests
import json
import ast
import time

class MyMQTT:
    def __init__(self, clientID, broker, port):
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self.payload = ''

        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        payload = msg.payload
        message_obj = ast.literal_eval(payload.decode("utf-8"))
        value = message_obj['value']
        device = 'gas'
        if device == "gas":
            #threshold = float(requests.get(resource_address + "get_threshold&deviceid=" + device_id).json())
            threshold = 1
            if int(value) > threshold:
                #pub_topic = requests.get(resource_address + "get_topic_gas_strategy").json()
                pub_topic='ALTRO_PUB'
                msg = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS GAS VALUE HAS BEEN DETECTED!!! CHECK IF YOU TURNED"  \
                       " OFF THE GAS!!!"
                self.myPublish(pub_topic, json.dumps({"new": msg}))

    def mySubscribe (self, topic):
        # if needed, you can do some computation or error-check before subscribing
        print ("subscribing to %s" % (topic))
        # subscribe for a topic
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic

    def start(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()

    def stop(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

    def myPublish (self, topic, msg):
        #self._isSubscriber = False
        print("publishing '%s' with topic '%s'"%(msg, topic))
        # publish a message with a certain topic

        self._paho_mqtt.publish(topic, msg, 2)
        #global publish_time
        #publish_time = json.load(msg)['time']

if __name__ == "__main__":
    # service_address = "0.0.0.0:8080/"
    # resource_address = requests.get(service_address + "get_resource").json()
    # broker = requests.get(service_address + "get_borker").json()
    # port = requests.get(service_address + "get_port").json()
    # topic = requests.get(resource_address + "get_topic").json()

    broker = "192.168.1.147"  # mosquitto broker
    port = 1883
    topic = 'PUB_PROVA'

    ext_publisher = MyMQTT("hey", broker, port)
    ext_publisher.start()

    # gasStrategy = MyMQTT("gasStrategy", broker, port)
    # gasStrategy.start()
    # gasStrategy.mySubscribe(topic)  # All the topic you can have through requests
    gasStrategy = MyMQTT("gasStrategy", broker, port)
    gasStrategy.start()
    gasStrategy.mySubscribe(topic)  # All the topic you can have through requests

    i = 0
    while True:
        if i%3 == 0:
            ext_publisher.myPublish(topic=topic, msg=json.dumps({"value": 3}))
        else:
            ext_publisher.myPublish(topic=topic, msg=json.dumps({"value": 0}))

        time.sleep(5)
        i+=1


    gasStrategy.stop()