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

#path = os.getcwd()
#print(path)
path = "/"
class WebService():
    exposed = True

    def GET(self, *uri, **param):
        # with open(path+"index.html", 'r') as fp:
        #     index = fp.read()
        # print(uri, param)
        # return index
        return open("index.html", "r").read()

    def POST(self, *uri, **params):
        if uri[0] == 'saveDashboard':
            dash = json.loads(params["json_string"])  # Load json object
            with open(path+"dashboard.json", "w") as f:
                json.dump(dash, f, indent=2)  # Write json to file
            print(uri, params)


if __name__ == '__main__':
    conf = {'/':


        {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), '/')),
            'tools.staticdir.root': os.getcwd()
        },
        '/dashboard':
            {
                'tools.staticdir.on': True,
                #'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'dashboard.json'))
                'tools.staticdir.dir': "dashboard.json"

            },
        '/css':
            {
                'tools.staticdir.on': True,
                #'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './css'))
                'tools.staticdir.dir': "./css"

            },
        '/img':
            {
                'tools.staticdir.on': True,
                #'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './img'))
                'tools.staticdir.dir': "./img"

            },
        '/js':
            {
                'tools.staticdir.on': True,
                #'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './js'))
                'tools.staticdir.dir': "./js"

            },
        '/plugins':
            {
                'tools.staticdir.on': True,
                #'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './plugins'))
                'tools.staticdir.dir': "./plugins"

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

