
import time
import requests
from imutils.video import WebcamVideoStream
import os
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

module_name = os.path.basename(__file__) # returns the current module name i.e. motion_pub.py
conf_file_name = module_name.split(sep='.')[0]+'_conf.json' # conf_file_name= motion_pub_conf.json

with open(conf_file_name, "r") as read_file:
    conf_file = json.load(read_file)
    camera_id = conf_file["camera_id"]
    pir_id = conf_file["pir_id"]
    room = conf_file["room"]
    VIDEO_SOURCE = conf_file["VIDEO_SOURCE"]
    photo_directory = conf_file["photo_directory"]
    service_cat_ip = conf_file["service_cat_ip"]
    service_cat_port = conf_file["service_cat_port"]


if __name__ == "__main__":


    broker = "192.168.1.147" # mosquitto broker
    port = 1883

    # start camara
    camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
    if not os.path.exists(photo_directory):
        os.makedirs(photo_directory)

    # create camera publisher
    camera_pub_topic = 'photo' #requests.get("http://192.168.1.254:8080/get_topic?id=house1_Kitchen_camera").json()
    camera_pub = MyMQTT(clientID=camera_id+'_publisher', topic=camera_pub_topic, broker=broker, port=port, isSubscriber=False)
    camera_pub.start()

    # create motion publisher
    motion_topic = 'motion_topic' #requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_motion").json()
    pub = MyMQTT(clientID=pir_id, topic=motion_topic, broker=broker, port=port, isSubscriber=False)
    pub.start()



    i = 0
    motion = 0
    while True:

        if i % 2 == 0:
            motion = 1
        else:
            motion = 0
        if motion:
            pub.myPublish(msg=json.dumps({"DeviceID": "house1_Kitchen_motion", "value": motion, "time": time.time()}))
            frame = camera.read()
            now = time.time()
            np_listed = frame.tolist()
            print('len', len(np_listed))
            camera_pub.myPublish(msg=json.dumps({"array_": np_listed, "time": now, "room": room}))
            # When you send your msg to your broker, you must empty payload, otherwise it will be sent everytime when enter the loop


        print("value of pir :  ", motion)
        time.sleep(5)
        i += 1

    # time_pub.stop()
