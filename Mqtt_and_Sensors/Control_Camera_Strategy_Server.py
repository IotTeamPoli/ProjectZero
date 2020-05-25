#!/usr/bin/python
# -*- coding: utf-8 -*-
import cherrypy
import requests
import json
import time
from imutils.video import WebcamVideoStream

# scatta foto se riceve una get request
# get al resouce e metterci il proprio ip nella topic

"""

        get scatta foto sia da control sia da telegram.
        return con json

"""

# TODO cosa scrivere come IP_ADDRESS chiedere se va bene
# TODO videosource da config

FILENAME = "config_sensors.json"

# static read form file
with open(FILENAME, "r") as f:
    d = json.load(f)
    SERVICE_ADDRESS = d["servicecat_ip"]

    camera_ip = d["camera_ip"]
    camera_port = d["camera_port"]
    house_id = d["house_id"]
    room_id = d["room_id"]
    camera_id = d["camera_id"]

camera_address = "http://"+camera_ip+":"+str(camera_port)+"/"

# service_address = "0.0.0.0:8080/"
# resource_address = requests.get(service_address + "get_resource")
# camera_server_address =  it should know
# camera_server_port =  it should know

@cherrypy.expose
class CameraServer(object):
    def GET(self, *uri, **params):  # params can also be void
        ans = {}
        if uri[0] == "take_picture":
            # make foto
            VIDEO_SOURCE = 0  # dovrebbe leggerlo nel file di conf della camera (che è lo stesso del motion)
            camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
            frame = camera.read()
            now = time.time()
            np_listed = frame.tolist()
            print('len', len(np_listed))
            # TODO giulia save to database
            return json.dumps({"array_": np_listed})
        else:
            return json.dumps(ans)

def registration():
    """register to service catalog"""
    try:
        url = SERVICE_ADDRESS + "/" + "update_service"
        res = requests.get(url, {"id": house_id+"_"+room_id+"_"+camera_id, "ip": camera_ip, "port":camera_port})
        print("status: ", res.status_code)
    except Exception as e:
        print("failed: ", e)

if __name__ == '__main__':

    registration()
    cherrypy.config.update({'server.socket_host': camera_ip})
    cherrypy.config.update({'server.socket_port': camera_port})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    }
    cherrypy.tree.mount(CameraServer(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
