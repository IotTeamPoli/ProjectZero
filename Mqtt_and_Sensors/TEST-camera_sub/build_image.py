from Mqtt_and_Sensors.myMqtt_codes.my_mqtt import *
import time
import requests
import sys
import numpy as np
from imutils.video import WebcamVideoStream
from imutils import opencv2matplotlib
from PIL import Image
import socket
import io
import os
import json
import ast

sys.path.append("..")


def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()

def byte_array_to_pil_image(byte_array):
    return Image.open(io.BytesIO(byte_array))



# from conf file read the service catalogue ip
# from service catalogue get the resource catalogue ip
# from con file get id of camera


if __name__ == "__main__":


    sock = socket.create_connection(("test.mosquitto.org", 1883))
    socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

    broker = remoteAdd[0]
    port = remoteAdd[1]

    # subscribe to pir_pub (motion sensor)
    #sub_topic = requests.get(resource_catalogue_ip+":"+port+"/get_topic?id="+pir_id).json()
    photo_topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
    sub_ = MyMQTT(clientID='_subscriber', topic=photo_topic, broker=broker, port=port, isSubscriber=True)
    sub_.start()
    sub_.mySubscribe()

    while True:
        payload_obj = sub_.payload
        # time.sleep(15)
        if payload_obj:
            object = ast.literal_eval(payload_obj.decode("utf-8")) # class 'bytes'
            np_array_RGB = np.array(object['array'])
            rec_time = object['time']
            if time.time()-rec_time>3:
                print('motion detected')
                image = Image.fromarray(np_array_RGB)  #  PIL image
                image.show(image)
                print('showed')

