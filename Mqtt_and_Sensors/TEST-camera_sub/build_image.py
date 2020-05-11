from Mqtt_and_Sensors.myMqtt_codes.my_mqtt import *
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

sys.path.append("..")


if __name__ == "__main__":


    sock = socket.create_connection(("test.mosquitto.org", 1883))
    socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

    broker = remoteAdd[0]
    port = remoteAdd[1]

    photo_topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
    sub_ = MyMQTT(clientID='boo_subscriber', topic=photo_topic, broker=broker, port=port, isSubscriber=True)
    sub_.start()
    sub_.mySubscribe()
    sub_.start()


    while True:
        payload_obj = sub_.payload
        #time.sleep(10)
        if payload_obj:
            print(payload_obj)
            object_ = ast.literal_eval(payload_obj.decode("utf-8"))
            image_array = np.asarray(object_['array_'], np.uint8)
            rec_time = object_['time']
            #if time.time()-rec_time>1:
            image = Image.fromarray(image_array, 'RGB')  #  PIL image
            image.save(str(time.time())+'.jpg')
            image.show(image)
            print('showed')
            # empty the payload after using the content.
            sub_.payload = None