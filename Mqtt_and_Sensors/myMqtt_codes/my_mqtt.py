import paho.mqtt.client as PahoMQTT
import json


class MyMQTT:
    def __init__(self, clientID, topic, broker, port, isSubscriber):
        self.broker = broker
        self.port = port
        #self.notifier = notifier
        self.clientID = clientID

        # self._topic = "iot.eclipse.org"
        self._topic = topic
        self._isSubscriber = isSubscriber
        self._isPublisher = not self._isSubscriber
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID, False)

        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        if isSubscriber:
            self._paho_mqtt.on_message = self.myOnMessageReceived

    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))

    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        #self.notifier.notify(msg.topic, msg.payload)
        print('data received successfully!')
        # the motion payload is a json: msg = json.dumps({"DeviceID": "house1_Kitchen_motion", "value": pir.value}
        self.payload = msg.payload


    def returned_payload(self):
        return (self.payload())


    def myPublish (self, msg):
        self._isSubscriber = False
        topic = self._topic
        # if needed, you can do some computation or error-check before publishing
    	print ("publishing '%s' with topic '%s'" % (msg, topic))
        # publish a message with a certain topic
    	self._paho_mqtt.publish(topic, msg, 2)
        global publish_time
        publish_time = json.load(msg)['time']


    def mySubscribe (self):
        # if needed, you can do some computation or error-check before subscribing
        topic = self._topic
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