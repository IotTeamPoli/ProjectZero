#!/usr/bin/python
# -*- coding: utf-8 -*-
import cherrypy
import requests
import json
import time
from imutils.video import WebcamVideoStream
import os
from os import listdir
from PIL import Image
import datetime
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
    VIDEO_SOURCE = d["VIDEO_CAMERA_SOURCE"]
    camera_ip = d["camera_ip"]
    camera_port = d["camera_port"]
    house_id = d["house_id"]
    room_id = d["room_id"]
    camera_id = d["camera_id"]
    photo_directory = d["photo_directory"]

camera_address = "http://"+camera_ip+":"+str(camera_port)+"/"

saving_path = house_id+'/'+photo_directory
if not os.path.exists(saving_path):
    os.makedirs(saving_path)

# service_address = "0.0.0.0:8080/"
# resource_address = requests.get(service_address + "get_resource")
# camera_server_address =  it should know
# camera_server_port =  it should know

@cherrypy.expose
class CameraServer(object):
    def GET(self, *uri, **params):  # params can also be void
        ans = {}
        if uri[0] == "take_picture": # makes the picture when called
            try:
                # make foto
                camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
                frame = camera.read()
                now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                #now = time.time()

                # from array to PIL image
                image = Image.fromarray(frame, 'RGB')  #  PIL image
                name = room_id+'_'+str(now) + '.jpg'

                # save in directory
                image.save(saving_path+name)

                # response message
                msg = saving_path+name
                return json.dumps({"msg": msg})
            except Exception as e:
                ans = {'response': 'an error occured'}
                return json.dumps(ans)

        elif uri[0] == 'get_history': # returns the list of all the pictures taken
            print('entered')
            imagesList = os.listdir(saving_path)
            loadedImages = []
            [loadedImages.append(saving_path+x) for x in imagesList]
            if loadedImages:
                msg = loadedImages
            else:
                msg = 'Nothing to show.'
            return json.dumps({"msg": msg})



        elif uri[0]== 'get_photo_day': # returns a list of the photo made in a specific day
            # http://ip+port/get_photo_day?year=value&month=value&day=value
            # returns all the photo of that day
            year = params['year']
            month = params['month']
            day = params['day']
            check_day = str(year)+'-'+str(month)+'-'+str(day)

            imagesList = os.listdir(saving_path)
            loadedImages = []
            [loadedImages.append(saving_path + x) for x in imagesList if check_day in x]

            if not imagesList:
                msg = 'Nothing to show. Directory is empty.'
            elif loadedImages:
                msg = loadedImages
            else:
                msg = 'Nothing to show. No pics taken in '+check_day
            return json.dumps({"msg": msg})

        else:
            ans ={'response': 'invalid request'}
            return json.dumps(ans)

    def DELETE(self, *uri, **params):
        msg =''
        if uri[0] == 'delete_all': # delete all the pictures in history
            imagesList = os.listdir(saving_path)
            print(imagesList)
            if imagesList:
                for img in imagesList:
                    os.remove(saving_path+img)
                msg = 'All the pics have been removed successfully.'
            else:
                msg = 'Nothing to delete. Directory is already empty.'


        elif uri[0] == 'delete_day':
            # http://ip+port/delete_day?year=value&month=value&day=value
            # delete all the photo of that day
            year = params['year']
            month = params['month']
            day = params['day']
            delete_day = str(year) + '-' + str(month) + '-' + str(day)

            imagesList = os.listdir(saving_path)
            if imagesList:
                to_delete = []
                [to_delete.append(saving_path + x) for x in imagesList if delete_day in x]
                if to_delete:
                    for img in to_delete:
                        os.remove(img)

                    msg = 'Pics taken in '+delete_day+' have been removed successfully'
                else:
                    msg = 'Nothing to delete. No pics taken in '+delete_day
            else:
                msg = 'Nothing to delete. Directory is already empty.'

        return (json.dumps({'msg':msg}))




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
