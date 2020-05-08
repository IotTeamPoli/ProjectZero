import paho.mqtt.client as PahoMQTT
import datetime
import json
import time
import datetime
import requests
import sys
from imutils.video import WebcamVideoStream
from imutils import opencv2matplotlib
from PIL import Image
import os
import socket
import io
import matplotlib.pyplot as plt
import os

sys.path.append("..")


def pil_image_to_byte_array(image):
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, "PNG")
    return imgByteArr.getvalue()

def byte_array_to_pil_image(byte_array):
    return Image.open(io.BytesIO(byte_array))




FPS = 1 # FPS = frame per second
VIDEO_SOURCE = 0


if __name__ == "__main__":
    camera = WebcamVideoStream(src=VIDEO_SOURCE).start()

    # broker = requests.get("http://127.0.0.1:8080/get_broker").json()
    # port = requests.get("http://127.0.0.1:8080/get_port").json()
    # topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
    # print(broker,port,topic)
    #
    # sock = socket.create_connection(("test.mosquitto.org", 1883))
    # socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    # remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)
    #
    # broker = remoteAdd[0]
    # port = remoteAdd[1]

    # Open camera
    # src=VIDEO_SOURCE=0 is the computer webcam. if a camera is attached throug usb, the
    # webcam becomes src=1 and the new camera becomes src=0

    while True:
        motion = [0,1,0,1,0] # sub from motion.
        i = 0
        for signal in motion:
            if signal==1:
                frame = camera.read()
                np_array_RGB = opencv2matplotlib(frame)  # Convert to RGB
                image = Image.fromarray(np_array_RGB)  #  PIL image
                # res = requests.get("127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
                # new = topic.split('/')
                # new_ = new[2:]
                # new_topic = '/'.join([str(elem) for elem in new_])

                directory = 'captures/'+str(i)
                if not os.path.exists(directory):
                    os.makedirs(directory)

                with open(directory+'.jpg', 'w') as f:
                    image.save(f)
                print('saved')
            #     frame = camera.read()
            #     plt.imshow(opencv2matplotlib((frame))) #  PIL image
            #     plt.savefig('ioteam/' + str(i) + '.jpg')
            #     print('saved')
            time.sleep(3)

