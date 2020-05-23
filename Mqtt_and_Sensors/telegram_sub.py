import telegram
import time
import numpy as np
from PIL import Image
import socket
import io
import paho.mqtt.client as PahoMQTT
import ast
import sys
import Client.BotObject


TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"
myurl = "http://127.0.0.1:"
port_pre = "8081"
port_res = "8080"
bot = telegram.Bot(token=TOKEN)



broker = "192.168.1.147"  # mosquitto broker
port = 1883

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
        if self.payload:
            object_ = ast.literal_eval(self.payload.decode("utf-8"))
            image_array = np.asarray(object_['array_'], np.uint8)
            rec_time = object_['time']
            # if time.time()-rec_time>1:
            image = Image.fromarray(image_array, 'RGB')  #  PIL image
            now = time.time()
            image.save('photo_motion/' + str(now) + '.jpg')  # la folder di salvataggio dipende dall houseID
            print('image: ', type(image))
            with open('photo_motion/' + str(now) + '.jpg', 'rb') as f:
                print('hey')
                bot.send_photo(chat_id='128817114', photo=f)  # manda solo una immagine in memoria
                # giulia: 557427612
                # matteo 128817114
            # empty the payload after using the content.
            sub_.payload = None
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



#chat_id = requests.get(resource_server_and_port + "house_chat?id=" + house).json()["chatID"]
if __name__ == '__main__':
    photo_topic = "CAMERA"  # requests.get("http://192.168.1.254:8080/get_topic?id=house1_Kitchen_camera").json()
    sub_ = MyMQTT(clientID='telegram_sub', topic=photo_topic, broker=broker, port=port, isSubscriber=True)
    sub_.start()
    sub_.mySubscribe()
    sub_.start()

    while True:
        time.sleep(1)

    sub_.stop()
