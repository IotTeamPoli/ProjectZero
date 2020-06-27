#!/usr/bin/python
# -*- coding: utf-8 -*-
import cherrypy
import requests
import numpy as np
import json
import time
from imutils.video import WebcamVideoStream
import os
from os import listdir
from PIL import Image
import datetime
# scatta foto se riceve una get request
# get al resouce e metterci il proprio ip nella topic

# TODO cosa scrivere come IP_ADDRESS chiedere se va bene

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
    print(camera_id)

camera_address = "http://"+camera_ip+":"+str(camera_port)+"/"

saving_path = house_id+'/motion_photo/'
if not os.path.exists(saving_path):
    os.makedirs(saving_path)

# service_address = "0.0.0.0:8080/"
# resource_address = requests.get(service_address + "get_resource")
# camera_server_address =  it should know
# camera_server_port =  it should know

@cherrypy.expose
class CameraServer(object):
    def __init__(self):
        pass
    
    def GET(self, *uri, **params):  # params can also be void
        service = CameraManager()
        ans = {}
        if uri[0] == "take_picture": # makes the picture when called
            try:
                listed_frame = service.take_picture()
                json.dumps({"msg": listed_frame})
                # # make foto
                # camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
                # frame = camera.read()
                # #now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                #
                # # response message
                # return json.dumps({"msg": frame.tolist()})

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
        listed = frame.tolist
        return (listed)

def registration():
    """register to service catalog"""
    try:
        url = SERVICE_ADDRESS + "update_service?id="+camera_id+"&ip="+camera_ip+"&port="+str(camera_port)
        res = requests.get(url)
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
