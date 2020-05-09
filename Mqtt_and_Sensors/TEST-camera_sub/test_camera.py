from Mqtt_and_Sensors.myMqtt_codes.my_mqtt import *
import time
import requests
import sys
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

module_name = os.path.basename(__file__)
conf_file_name = module_name.split(sep='.')[0]+'_conf.json'

with open(conf_file_name, "r") as read_file:
    conf_file = json.load(read_file)
    camera_id = conf_file["id"]
    room = conf_file["room"]
    VIDEO_SOURCE = conf_file["VIDEO_SOURCE"]
    photo_directory = conf_file["photo_directory"]
    service_cat_ip = conf_file["service_cat_ip"]
    service_cat_port = conf_file["service_cat_port"]


if __name__ == "__main__":
    camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
    if not os.path.exists(photo_directory):
        os.makedirs(photo_directory)


    sock = socket.create_connection(("test.mosquitto.org", 1883))
    socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

    broker = remoteAdd[0]
    port = remoteAdd[1]

    # subscribe to pir_pub (motion sensor)
    #sub_topic = requests.get(resource_catalogue_ip+":"+port+"/get_topic?id="+pir_id).json()
    sub_topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_motion").json()
    camera_subscriber = MyMQTT(clientID=camera_id+'_subscriber', topic=sub_topic, broker=broker, port=port, isSubscriber=True)
    camera_subscriber.start()
    camera_subscriber.mySubscribe()


    # create camera publisher
    pub_topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_Kitchen_camera").json()
    camera_pub = MyMQTT(clientID=camera_id+'_publisher', topic=pub_topic, broker=broker, port=port, isSubscriber=False)
    camera_pub.start()

    while True:
        payload_obj = camera_subscriber.payload
        time.sleep(15)
        if payload_obj:
            object = ast.literal_eval(payload_obj.decode("utf-8")) # class 'bytes'
            motion = object['value']
            rec_time = object['time']
            if motion == 1 and time.time()-rec_time>3:
                print('motion detected')
                frame = camera.read()
                now = time.time()
                np_array_RGB = opencv2matplotlib(frame)
                np_listed = np_array_RGB.tolist()
                camera_pub.myPublish(msg = json.dumps({"array": np_listed, "time": now, "room": room}))
                #camera_pub.myPublish(msg = bytes(frame))
                # image = Image.fromarray(np_array_RGB)  #  PIL image
                # with open(photo_directory + "house_id_"+ str(now) + '.jpg', 'w') as f:
                #     image.save(f)
                # print('saved')


