#!/usr/bin/python
# -*- coding: utf-8 -*-
import cherrypy
import requests
import json

# service_address = "0.0.0.0:8080/"
# resource_address = requests.get(service_address + "get_resource")
# motion_server_address = requests.get(service_address + "get_motion_server_address")
# motion_server_port = requests.get(service_address + "get_motion_server_port")

@cherrypy.expose
class MotionServer(object):
    def GET(self, *uri, **params):
        ans = {}
        if uri[0] == "motion_strategy":
            value = float(params["value"])
            if value > float(params["threshold"]) and params["status"] == "ON":
                ans["text"] = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS MOVEMENT HAS BEEN DETECTED!!!"
            else:
                ans["text"] = "OK"
        return json.dumps(ans)

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': "localhost"})  #
    cherrypy.config.update({'server.socket_port': 8080})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        }
    }
    cherrypy.tree.mount(MotionServer(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()