# // TO DO: autoload di dashboard.json


import cherrypy
import json
import os
import socket
import requests

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
# print("Your Computer Name is:" + hostname)
print("Your Computer IP Address is:" + IPAddr)

# path = os.getcwd()
# print(path)
#path = "./"


class WebService(object):
    exposed = True
    @cherrypy.tools.json_out()

    def GET(self, *uri, **param):
        with open("./index.html") as fp:
            index = fp.read()
        return index

    def POST(self, *uri, **params):
        if uri[0] == 'saveDashboard':
            print('URI: ', uri[0])
            print('params: ', params)
            dash = json.loads(params["json_string"])  # Load json object
            with open("./dashboard_prova.json", "w") as f:
                json.dump(dash, f, indent=2)  # Write json to file
            print(uri, params)


            # if uri[0] == "saveDashboard":
            #     path = "./"
            #     with open(path + "dashboard.json", "w") as file:
            #         file.write(params['json_string'])


if __name__ == '__main__':
    conf = {'/':

        {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './')),
            'tools.staticdir.root': os.getcwd()
        },
        '/css':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "./css"

            },
        '/img':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "./img"

            },
        '/js':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "./js"

            },
        '/dashboard':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "./dashboard.json"

            },
        '/plugins':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "./plugins"

            },

        '/index':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir' : "./",
                'tools.staticdir.index' : "index.html",

            },
        # '/static':
        #     {
        #         'tools.staticdir.on': True,
        #         'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard'))
        #     }
    }
    cherrypy.tree.mount(WebService(), '/', config=conf)
    cherrypy.config.update({'server.socket_host': "127.0.0.1"})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.config.update(conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
