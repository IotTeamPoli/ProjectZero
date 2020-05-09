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
        self._paho_mqtt.subscribe(self._topic, 2)
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