import cherrypy
import json
import os

class WebService(object):
    exposed = True
    @cherrypy.tools.json_out()

    def GET(self, *uri, **param):
        with open("./index.html") as fp:
            index = fp.read()
        return index

    def POST(self, *uri, **params):
        if uri[0] == 'saveDashboard':
            dash = json.loads(params["json_string"])  # Load json object
            with open("./dashboard_prova.json", "w") as f:
                json.dump(dash, f, indent=2)  # Write json to file
            print(uri, params)


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

            }
    }
    cherrypy.tree.mount(WebService(), '/', config=conf)
    cherrypy.config.update({'server.socket_host': "127.0.0.1"})
    cherrypy.config.update({'server.socket_port': 8087})
    cherrypy.config.update(conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
