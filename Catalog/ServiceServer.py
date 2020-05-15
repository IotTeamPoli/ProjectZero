import cherrypy
from Catalog import IoTCatalogue
import json


service_manager = IoTCatalogue.ServiceManager()
class CatalogueWebService(object):
    exposed = True
    def GET(self,*uri,**params):
        try:
            if(uri[0]=='print_all_services'):
                """ - print_all_services (no other param needed):returns all the resource catalog
                       service_catalog = requests.get("http://127.0.0.1:8080/print_all_services").json()"""
                result = service_manager.print_all_services()
            elif(uri[0]=='search_service'):
                result = service_manager.search_service(params['id'])
            elif(uri[0]=='update_service'):
                result = service_manager.update_service(params['id'],params['port'],params['ip'])            
            elif(uri[0]=='get_ip'):
                result = service_manager.get_ip(params['id'])
            elif(uri[0]=='get_port'):
                result = service_manager.get_port(params['id'])
            elif(uri[0]=='get_lastseen'):
                result = service_manager.get_lastseen(params['id'])
            return result

        except:
            return json.dumps("Ooops! there was an error")
        
if __name__ == '__main__':

    cherrypy.config.update({'server.socket_host': '192.168.1.254'})
    cherrypy.config.update({'server.socket_port': 8080})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            # 'tools.session.on': True,
            }
        }
    cherrypy.tree.mount(CatalogueWebService(),'/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


        # netstat -ano | findstr :PORTA
        # taskkill /PID PROCESSID /F