#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
# import telegram
import requests
from PIL import Image
import io
import json
import sys
import time
from Mqtt_and_Sensors.myMqtt_codes import my_mqtt
import socket
import numpy as np

def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()


def byte_array_to_pil_image(byte_array):
    return Image.open(io.BytesIO(byte_array))


sock = socket.create_connection(("test.mosquitto.org", 1883))
socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

broker = remoteAdd[0]
port = remoteAdd[1]

camera_id = ''
photo_topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
telegram_subscriber = my_mqtt.MyMQTT(clientID="telegram_sub_" + 'camera_id', topic=photo_topic, broker=broker,
                                     port=port, isSubscriber=True)
telegram_subscriber.start()
telegram_subscriber.mySubscribe()

payload_obj = telegram_subscriber.payload
last_update = payload_obj['time']
np_array_RGB = np.array(payload_obj['bytes']) # bytes to recostruct the image

# bot solo per inizializare
TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"
myurl = "http://127.0.0.1:"
port_pre = "8081"
port_res = "8080"


def start(update, context):
    TEXT = '''
    This is the presence bot of the IoT360 managed houses, 
    welcome to the IoT360 house u can use this list of command!!!
    /start
    /get_image
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text=TEXT)
    print("chat id", update.effective_chat.id)


def get_image(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="checking")
    text_msg = "last photo was taken at: "+payload_obj['time']
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_msg)

    image = Image.fromarray(np_array_RGB)  #  PIL image
    with open(image, 'rb') as f:
        context.bot.send_photo(chat_id=update.effective_chat.id, photo= f) #open(image, 'rb'))


def main():


    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    # List of handlers:
    start_handler = CommandHandler('start', start)

    if time.time() - last_update<60:
        check_handler = CommandHandler('get_image', get_image)

    # List of dispatchers
    dp.add_handler(start_handler)
    dp.add_handler(check_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

