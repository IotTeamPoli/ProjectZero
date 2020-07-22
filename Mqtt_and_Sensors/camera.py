import cherrypy
import requests
import json
import time
from imutils.video import WebcamVideoStream
import os


# takes picture when requested

FILENAME = "config_sensors.json"

# static read form file
with open(FILENAME, "r") as f:
    d = json.load(f)
    SERVICE_ADDRESS = d["servicecat_ip"]
    VIDEO_SOURCE = d["VIDEO_CAMERA_SOURCE"]
    camera_ip = d["camera_ip"]
    camera_port = d["camera_port"]
    house_id = d["house_id"]
    room_id = d["room_id"]
    camera_id = d["camera_id"]
    mqtt_interval = d["mqtt_interval"]

camera_address = "http://" + camera_ip + ":" + str(camera_port) + "/"

saving_path = house_id + '/motion_photo/'
if not os.path.exists(saving_path):
    os.makedirs(saving_path)


class CameraServer(object):
    def __init__(self):
        pass

    exposed = True

    def GET(self, *uri, **params):  # params can also be void
        service = CameraManager()
        if uri[0] == "take_picture":  # takes the picture when called
            try:
                listed_frame = service.take_picture()
                return (json.dumps({"msg": listed_frame}))
            except Exception as e:
                ans = {'msg': 'an error occured in camera server'}
                return json.dumps(ans)


class CameraManager(object):
    def __init__(self):
        pass

    def take_picture(self):
        # make foto
        camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
        frame = camera.read()
        # to get a json seriezable format of frame it has to be an array
        listed = frame.tolist()
        return (listed)


def registration(address, catalog_id, ip, port):
    """register to service catalog"""
    try:
        url = address + "update_service?id=" + catalog_id + "&ip=" + ip + "&port=" + str(port)
        res = requests.get(url).json()
        print(res)
    except Exception as e:
        print("Failed connection with Service Catalog: ", str(e))


if __name__ == '__main__':

    cherrypy.config.update({'server.socket_host': camera_ip})
    cherrypy.config.update({'server.socket_port': camera_port})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    }
    cherrypy.tree.mount(CameraServer(), '/', conf)
    cherrypy.engine.start()
    while True:
        try:
            registration(SERVICE_ADDRESS, camera_id, camera_ip, camera_port)
            time.sleep(mqtt_interval)
        except Exception as e:
            print("Connection to service catalog failed with error: ", str(e))
    cherrypy.engine.block()
