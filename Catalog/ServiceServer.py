import cherrypy
import IoTCatalogue
import json

service_manager = IoTCatalogue.ServiceManager()


class CatalogueWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        try:
            if (uri[0] == 'print_all_services'):
                """ - print_all_services (no other param needed):returns all the resource catalog
                       service_catalog = requests.get("http://127.0.0.1:8080/print_all_services").json()"""
                result = service_manager.print_all_services()
            elif (uri[0] == 'get_address'):  # returns a dictionary with cat id,ip,port
                result = service_manager.get_address(params["id"])
            elif (uri[0] == 'search_service'):
                result = service_manager.search_service(params['id'])
            elif (uri[0] == 'update_service'):
                result = service_manager.update_service(params['id'], params['ip'], params['port'])
                save = service_manager.save_all()
            elif (uri[0] == 'delete_service'):
                result = service_manager.delete_service(params['id'])
                save = service_manager.save_all()
            elif (uri[0] == 'get_ip'):
                result = service_manager.get_ip(params['id'])
            elif (uri[0] == 'get_port'):
                result = service_manager.get_port(params['id'])
            elif (uri[0] == 'get_lastseen'):
                result = service_manager.get_lastseen(params['id'])
            elif (uri[0] == 'get_broker'):
                """ - get_broker (no parmeter needed): return the IP address of the message broker

                        broker_ip = requests.get("http://127.0.0.1:8080/get_broker").json()  """
                result = service_manager.get_broker()
            elif (uri[0] == 'get_broker_port'):
                """ - get_port (no other param needed): return the port number for the broker
                       N.B. the following request already output an integer!

                       mqtt_port = requests.get("http://127.0.0.1:8080/get_port").json()  """
                result = service_manager.get_boroker_port()
            return result

        except:
            return json.dumps("Ooops! there was an error")


if __name__ == '__main__':
    ser_file = "ServiceCatalogue.json"
    ser_op = open(ser_file, 'r')
    ser = ser_op.read()
    ser_op.close()
    service = json.loads(ser)

    cherrypy.config.update({'server.socket_host': service['ip']})
    cherrypy.config.update({'server.socket_port': service['port']})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            # 'tools.session.on': True,
        }
    }
    cherrypy.tree.mount(CatalogueWebService(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()

    # netstat -ano | findstr :PORTA
    # taskkill /PID PROCESSID /F
