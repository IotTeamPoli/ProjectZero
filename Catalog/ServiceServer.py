import cherrypy
import IoTCatalogue
import json
import time
from datetime import datetime

service_manager = IoTCatalogue.ServiceManager()

""" N.B. When a service is added or disconnected, the last_seen field of the catalog is updated.
        When an existing service refreshes its subscription to the service catalog, its last_seen field is updated.
        If the last_seen field is expired, the service is automatically deleted from the list"""


class CatalogueWebService(object):
    exposed = True

    def GET(self, *uri, **params):
        try:
            if (uri[0] == 'print_all_services'):
                """ - print_all_services (no other param needed):returns all the service catalog
                       service_catalog = requests.get("http://127.0.0.1:8080/print_all_services").json()"""
                result = service_manager.print_all_services()
            elif (uri[0] == 'get_address'):
                """ get_address (id) returns a dictionary with id,ip,port of the searched service """
                result = service_manager.get_address(params["id"])
            # elif (uri[0] == 'search_service'):
            #     """ search_service (id) returns a dictionary with id,ip,port,lastseen of the searched service """
            #     result = service_manager.search_service(params['id'])
            elif (uri[0] == 'update_service'):
                """ update_service(id,ip,port): if a service is present in the list, updates the last_seen field.
                Otherwise adds a new service and updates the last_update field """
                result = service_manager.update_service(params['id'], params['ip'], int(params['port']))
                save = service_manager.save_all()
                print(save)
            elif (uri[0] == 'disconnect_service'):
                """ disconnect_service(id): deletes a service from the list and updates the last_update field """
                result = service_manager.disconnect_service(params['id'])
                save = service_manager.save_all()
                print(save)
            elif (uri[0] == 'get_ip'):
                """ returns the ip address of a given service """
                result = service_manager.get_ip(params['id'])
            elif (uri[0] == 'get_port'):
                """ returns the port of a given service """
                result = service_manager.get_port(params['id'])
            elif (uri[0] == 'get_lastseen'):
                """ returns the lastseen field of a given service """
                result = service_manager.get_lastseen(params['id'])
            elif (uri[0] == 'get_broker'):
                """ - get_broker (no parmeter needed): return the IP address of the message broker
                        broker_ip = requests.get("http://127.0.0.1:8080/get_broker").json()  """
                result = service_manager.get_broker()
            elif (uri[0] == 'get_broker_port'):
                """ - get_port (no other param needed): return the port number for the broker
                       N.B. the following request already outputs an integer!
                       mqtt_port = requests.get("http://127.0.0.1:8080/get_port").json()  """
                result = service_manager.get_broker_port()
            return result

        except:
            return json.dumps("Ooops! there was an error")


if __name__ == '__main__':
    ser_file = "ServiceCatalogue.json"
    ser_op = open(ser_file, 'r')
    ser = ser_op.read()
    ser_op.close()
    service = json.loads(ser)
    loopNum = 6
    deltaTsleep = 60 * 1
    deltaTfresh = 60 * 3  # timeout for service expiration

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

    while loopNum > 0:
        time.sleep(deltaTsleep)
        print('Service catalog checking freshness')

        ser_op = open(ser_file, 'r')
        ser = ser_op.read()
        ser_op.close()
        service = json.loads(ser)

        count = 0

        for s in service['service_list']:
            count += 1
            now = time.time()
            interval = now - s['last_seen']
            if interval > deltaTfresh:
                name = s['id']
                service['service_list'].pop(count - 1)
                service['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')

                out_file = open(ser_file, 'w')
                out_file.write(json.dumps(service, indent=4))
                out_file.close()

                print('%s disconnected: expired time' % name)

        loopNum -= 1

    cherrypy.engine.block()

    # netstat -ano | findstr :PORTA
    # taskkill /PID PROCESSID /F
