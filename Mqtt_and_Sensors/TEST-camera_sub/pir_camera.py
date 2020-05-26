import paho.mqtt.client as PahoMQTT
import datetime
import json
import time
from gpiozero import MotionSensor
import sys
import requests

import time
import requests
from imutils.video import WebcamVideoStream
import os
import paho.mqtt.client as PahoMQTT
import json


# broker = 'iot.eclipse.org'
# broker = request dal catalogo
# porta = request dal catalogo
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

with open('conif_sensors.json', "r") as read_file:
    conf_file = json.load(read_file)
    camera_id = conf_file["camera_id"]
    pir_id = conf_file["pir_id"]
    room = conf_file["pir_camera_room"]
    VIDEO_SOURCE = conf_file["VIDEO_CAMERA_SOURCE"]
    photo_directory = conf_file["photo_directory"]
    service_cat_ip = conf_file["service_cat_ip"]
    service_cat_port = conf_file["service_cat_port"]


if __name__ == "__main__":
    FILENAME = "../config_sensors.json"
    with open(FILENAME, "r") as f:
        d = json.load(f)
        PORT = d["IoTCatalogue_port"]
        IP_RASP = d["ip_raspberry"]
    from_config = IP_RASP + ":" + PORT
    broker = requests.get("http://"+from_config+"/get_broker").json()
    port = requests.get("http://"+from_config+"/get_port").json()
    topic_motion = requests.get("http://"+from_config+"/get_topic?id=house1_Kitchen_motion").json()


    # motion publisher
    pir_pub = MyMQTT(clientID="Motion", topic=topic_motion, broker=broker, port=port, isSubscriber=False)
    pir_pub.start()
    pir = MotionSensor(18, queue_len=30, sample_rate=1)


    # camera publisher
    # start camara
    # camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
    # if not os.path.exists(photo_directory):
    #     os.makedirs(photo_directory)
    #
    # # create camera publisher
    # camera_pub_topic = 'CAMERA' #requests.get("http://192.168.1.254:8080/get_topic?id=house1_Kitchen_camera").json()
    # camera_pub = MyMQTT(clientID=camera_id+'_publisher', topic=camera_pub_topic, broker=broker, port=port, isSubscriber=False)
    # camera_pub.start()

    while True:

        pir_pub.myPublish(json.dumps({"DeviceID": "house1_Kitchen_motion", "value": pir.value}))
        print("value of pir :  ")
        print(pir.value)
        # if pir.value:
        #     frame = camera.read()
        #     now = time.time()
        #     np_listed = frame.tolist()
        #     print('len', len(np_listed))
        #     camera_pub.myPublish(msg=json.dumps({"array_": np_listed, "time": now, "room": room}))

        time.sleep(30)

    time_pub.stop()
