import time
import codecs
import requests
import sys
import numpy as np
from imutils.video import WebcamVideoStream
from imutils import opencv2matplotlib
from PIL import Image
import socket
import io

import ast


import paho.mqtt.client as PahoMQTT
import json
import ast
import sys


class MyMQTT:
    def __init__(self, clientID, topic, broker, port, isSubscriber):
        self.broker = broker
        self.port = port
        #self.notifier = notifier
        self.clientID = clientID
        self.payload = ''

        # self._topic = "iot.eclipse.org"
        self._topic = topic
        self._isSubscriber = isSubscriber
        self._isPublisher = not isSubscriber
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        self.payload = msg.payload
        print('data received successfully!')



    def myPublish (self, msg):
        #self._isSubscriber = False
        print("publishing '%s' with topic '%s'"%(msg, self._topic))
        # publish a message with a certain topic
        print('total size: ', sys.getsizeof(msg))

        self._paho_mqtt.publish(self._topic, msg, 2)
        #global publish_time
        #publish_time = json.load(msg)['time']


    def mySubscribe (self):
        # if needed, you can do some computation or error-check before subscribing
        # print ("subscribing to %s" % (self._topic))
        # subscribe for a topic
        self._paho_mqtt.subscribe(self._topic, 0)
        # just to remember that it works also as a subscriber
        #self._isSubscriber = True


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

        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

sys.path.append("..")

if __name__ == "__main__":

    #sock = socket.create_connection(("test.mosquitto.org", 1883))
    #socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    #remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

    # broker = remoteAdd[0]
    # port = remoteAdd[1]
    broker = "192.168.1.147" # mosquitto broker
    port = 1883

    photo_topic = requests.get("http://192.168.1.254:8080/get_topic?id=house1_Kitchen_camera").json()
    sub_ = MyMQTT(clientID='boo_subscriber', topic=photo_topic, broker=broker, port=port, isSubscriber=True)
    sub_.start()
    sub_.mySubscribe()
    sub_.start()

    while True:
        payload_obj = sub_.payload
        # time.sleep(10)
        if payload_obj:
            print(payload_obj)
            object_ = ast.literal_eval(payload_obj.decode("utf-8"))
            image_array = np.asarray(object_['array_'], np.uint8)
            rec_time = object_['time']
            # if time.time()-rec_time>1:
            image = Image.fromarray(image_array, 'RGB')  #  PIL image
            image.save('photo_motion/'+str(time.time()) + '.jpg')
            image.show(image)
            print('showed')
            # empty the payload after using the content.
            sub_.payload = None
