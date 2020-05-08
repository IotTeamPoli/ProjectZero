from .myMqtt_codes.my_mqtt import *
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
    VIDEO_SOURCE = conf_file["VIDEO_SURCE"]
    photo_directory = conf_file["photo_directory"]
    service_cat_ip = conf_file["service_cat_ip"]
    service_cat_port = conf_file["service_cat_port"]

# i need to read the conf file of pir sensor in other to subscribe to it
with open("pir_con.json", "r") as read_file:
    pir_conf = json.load(read_file)
    pir_id = pir_conf['id']

if __name__ == "__main__":
    camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
    os.makedirs(photo_directory)

    # get resource_cat address from ServiceCat an then:
    resource_catalogue_ip = ''  # requests.get(service_catalogue_ip+":"+service_cat_port+"/get_ResCatIp").json()
    resource_catalogue_port = ''  # requests.get(service_catalogue_ip+":8080/get_ResCatPort").json() should return 8080
    broker = ''  # broker = requests.get(resource_catalogue_ip+":8080/get_broker").json()
    port = ''  # port = requests.get(resource_catalogue_ip+":8080/get_port").json() should return 1883
    pub_topic = ''   # pub_topic = requests.get(resource_catalogue_ip+":"+port+"/get_topic?id="+camera_id).json()


    sock = socket.create_connection(("test.mosquitto.org", 1883))
    socket_own_address = sock.getsockname()  # Return the socket’s own address. This is useful to find out the port number of an IPv4/v6 socket, for instance.
    remoteAdd = sock.getpeername()  # Return the remote address to which the socket is connected.  (" test.mosquitto.org", 1883)

    broker = remoteAdd[0]
    port = remoteAdd[1]

    # subscribe to pir_pub (motion sensor)
    sub_topic = requests.get(resource_catalogue_ip+":"+port+"/get_topic?id="+pir_id).json()
    camera_subscriber = MyMQTT(clientID=camera_id+'_subscriber', topic=sub_topic, broker=broker, port=port, isSubscriber=True)
    camera_subscriber.mySubscribe()
    camera_subscriber.start()

    # create camera publisher
    camera_pub = MyMQTT(clientID=camera_id+'_publisher', topic=pub_topic, broker=broker, port=port, isSubscriber=False)
    camera_pub.start()

    while True:
        payload_obj = camera_subscriber.returned_payload()
        payload = ast.literal_eval(payload_obj.encode("utf-8"))
        motion = payload['value']
        if motion:
            frame = camera.read()
            now = time.time()
            np_array_RGB = opencv2matplotlib(frame)
            camera_pub.myPublish(msg = json.dumps({"bytes": np_array_RGB, "time": now, "room": room}))
            image = Image.fromarray(np_array_RGB)  #  PIL image
            with open(photo_directory + "_"+ str(now) + '.jpg', 'w') as f:
                image.save(f)
            print('saved')

    # while True:
    #     motion = [0,1,0,1,0] # sub from motion.
    #     i = 0
    #     for signal in motion:
    #         if signal==1:
    #             frame = camera.read()
    #             np_array_RGB = opencv2matplotlib(frame)  # Convert to RGB
    #             image = Image.fromarray(np_array_RGB)  #  PIL image
    #             # res = requests.get(resource_catalogue_ip+":"+port+"/get_topic?id="+camera_id).json()
    #             # new = topic.split('/')
    #             # new_ = new[2:]
    #             # new_topic = '/'.join([str(elem) for elem in new_])
    #
    #
    #             with open(photo_directory+str(i)+'.jpg', 'w') as f:
    #                 image.save(f)
    #             print('saved')
    #         #     frame = camera.read()
    #         #     plt.imshow(opencv2matplotlib((frame))) #  PIL image
    #         #     plt.savefig('ioteam/' + str(i) + '.jpg')
    #         #     print('saved')
    #         time.sleep(3)

