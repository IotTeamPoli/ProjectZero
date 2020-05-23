#!/usr/bin/python
# -*- coding: utf-8 -*-
import cherrypy
import requests
import json
import time
from imutils.video import WebcamVideoStream


# service_address = "0.0.0.0:8080/"
# resource_address = requests.get(service_address + "get_resource")
# camera_server_address =  it should know
# camera_server_port =  it should know

@cherrypy.expose
class CameraServer(object):
    def GET(self, *uri, **params):  # params can also be void
        ans = {}
        if uri[0] == "camera_strategy":
            # make foto
            VIDEO_SOURCE = 0  # dovrebbe leggerlo nel file di conf della camera (che è lo stesso del motion)
            camera = WebcamVideoStream(src=VIDEO_SOURCE).start()
            frame = camera.read()
            now = time.time()
            np_listed = frame.tolist()
            print('len', len(np_listed))

            return json.dumps({"array_": np_listed})
        else:
            return json.dumps(ans)



if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': "localhost"})  #
    cherrypy.config.update({'server.socket_port': 8080})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    }
    cherrypy.tree.mount(CameraServer(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
