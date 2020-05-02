# // TO DO: autoload di dashboard.json


import cherrypy
import json
import os
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
# print("Your Computer Name is:" + hostname)
print("Your Computer IP Address is:" + IPAddr)


class WebIndex(object):
    exposed = True

    def GET(self, *uri, **param):
        with open("index.html") as fp:
            index = fp.read()
        print(uri, param)
        return index


class WebSave(object):
    def POST(self, *uri, **params):
        dash = json.loads(params["json_string"])  # Load json object
        with open("./dashboard.json", "w") as f:
            json.dump(dash, f, indent=2)  # Write json to file
        print(uri, params)


if __name__ == '__main__':
    conf = {'/':


        {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), '/'))
        },
        '/dashboard':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), 'dashboard.json'))
            },
        '/css':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './css'))
            },
        '/img':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './img'))
            },
        '/js':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './js'))
            },
        '/plugins':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './plugins'))
            },
        '/static':
            {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.abspath(os.path.join(os.path.dirname(__file__), './freeboard'))
            }
    }
    cherrypy.config.update({'server.socket_host': 'localhost'})
    cherrypy.config.update({'server.socket_port': 8083})
    cherrypy.tree.mount(WebIndex(), '/', config=conf)
    cherrypy.tree.mount(WebSave(), '/WebSave', config=conf)
    cherrypy.config.update(conf)
    cherrypy.engine.start()
    cherrypy.engine.block()

