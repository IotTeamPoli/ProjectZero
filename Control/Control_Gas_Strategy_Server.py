#!/usr/bin/python
# -*- coding: utf-8 -*-
import cherrypy
import requests
import json

# service_address = "0.0.0.0:8080/"
# resource_address = requests.get(service_address + "get_resource")
# gas_server_address = requests.get(service_address + "get_gas_server_address")
# gas_server_port = requests.get(service_address + "get_gas_server_port")

@cherrypy.expose
class GasServer(object):
    def GET(self, *uri, **params):
        ans = {}
        if uri[0] == "gas_strategy":
            value = float(params["value"])
            if value > float(params["threshold"]):
                ans["text"] = "⚠ ⚠ ⚠ WARNING ⚠ ⚠ ⚠\nAN ANOMALOUS GAS VALUE HAS BEEN DETECTED!!! CHECK IF YOU TURNED"  \
                       " OFF THE GAS!!!"
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
    cherrypy.tree.mount(GasServer(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()