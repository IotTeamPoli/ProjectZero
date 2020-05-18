#!/usr/bin/python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import time
import numpy as np
from PIL import Image
import socket
import io
import paho.mqtt.client as PahoMQTT
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

# camera_id = ''
# photo_topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
# telegram_subscriber = my_mqtt.MyMQTT(clientID="telegram_sub_" + 'camera_id', topic=photo_topic, broker=broker,
#                                      port=port, isSubscriber=True)
# telegram_subscriber.start()
# telegram_subscriber.mySubscribe()
#
# payload_obj = telegram_subscriber.payload
# last_update = payload_obj['time']
# np_array_RGB = np.array(payload_obj['bytes']) # bytes to recostruct the image

# bot solo per inizializare
TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"
myurl = "http://127.0.0.1:"
port_pre = "8081"
port_res = "8080"

broker = "192.168.1.147"  # mosquitto broker
port = 1883

#chat_id = requests.get(resource_server_and_port + "house_chat?id=" + house).json()["chatID"]

photo_topic = "CAMERA"  # requests.get("http://192.168.1.254:8080/get_topic?id=house1_Kitchen_camera").json()
sub_ = MyMQTT(clientID='telegram_sub', topic=photo_topic, broker=broker, port=port, isSubscriber=True)
sub_.start()
sub_.mySubscribe()
sub_.start()


def start(update, context):
    TEXT = '''
    This is the presence bot of the IoT360 managed houses, 
    welcome to the IoT360 house u can use this list of command!!!
    This bot will automatically send image if a motion is detected.
    /start
    
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text=TEXT)
    print("chat id", update.effective_chat.id)


# def get_image(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="checking")
#
#
#     image = Image.fromarray(np_array_RGB)  #  PIL image
#     with open(image, 'rb') as f:
#         context.bot.send_photo(chat_id=update.effective_chat.id, photo= f) #open(image, 'rb'))

def callback_camera(context):
    payload_obj = sub_.payload
    if payload_obj:
        print(payload_obj)
        object_ = ast.literal_eval(payload_obj.decode("utf-8"))
        image_array = np.asarray(object_['array_'], np.uint8)
        rec_time = object_['time']
        # if time.time()-rec_time>1:
        image = Image.fromarray(image_array, 'RGB')  #  PIL image
        now = time.time()
        image.save('photo_motion/' + str(now) + '.jpg') # la folder di salvataggio dipende dall houseID
        print('image: ', type(image))
        with open('photo_motion/'+str(now)+'.jpg', 'rb') as f:
            print('hey')
            context.bot.send_photo(chat_id='557427612', photo=f) # manda solo una immagine in memoria
            # giulia: 557427612
            # matteo 128817114
        # empty the payload after using the content.
        sub_.payload = None
    else:
        pass



def main():

    updater = Updater(token=TOKEN, use_context=True)
    job = updater.job_queue
    dp = updater.dispatcher
    # List of cmd
    start_handler = CommandHandler('start', start)
    #check_handler = CommandHandler('get_image', get_image)

    # List of dispatchers
    dp.add_handler(start_handler)
    #dp.add_handler(check_handler)

    # time.sleep(10)
    job_camera = job.run_repeating(callback_camera, interval=1, first=1) #
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

