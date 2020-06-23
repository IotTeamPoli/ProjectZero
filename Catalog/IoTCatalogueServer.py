import cherrypy
#from Catalog import IoTCatalogue
import IoTCatalogue
import json
import requests



resource_manager = IoTCatalogue.ResourceManager()
#service_manager = IoTCatalogue.ServiceManager()
#record = record_audio_video.Record()

class CatalogueWebService(object):
    """
     Here are some functions that other applications can call to receive the informations they need
     and/or modify the catalog itself. In the following list you can find also the request you need
     to write in your script so to receive the answer.

     Some functions require the identifier of house/room/device: how can you find it?
     Identifiers are built this way: myhouse_myroom_mydevice so house_id='myhouse'. room_id='myhouse_myroom', device_id='myhouse_myroom_mydevice'

     In practice you always need the id to address something (in case of the house,it coincides with the name), except when you are adding house/room
     (you pass the names separately so that the code can check the uniqueness and build an identifier)
    """
    def __init__(self):
        
        self.config_file = 'configuration.json'
        config=open(self.config_file,'r')
        configuration=config.read()
        config.close()
        self.config=json.loads(configuration)
        self.service_address = self.config['servicecat_address']
        
    
    exposed = True
    def GET(self,*uri,**params):
        try:
            if(uri[0]=='get_topic'):
                """ - get_topic (need to specify an id) this will return the mqtt_topic
                        there a 4 cases:
                        0- you pass as a parameter 'ResourceCatalogue' :returns the topic of the entire catalog
                        1- you pass as a parameter the id of the house: returns the topic of the house
                        2- you pass as a parameter the id of a room: returns the topic of the room
                        3- you pass as a parameter the id of a device:returns the topic of the device

                        topic = requests.get("http://127.0.0.1:8080/get_topic?id=house1_room1_camera").json()  """
                param = params["id"]
                result = resource_manager.get_topic(param)
                
            elif(uri[0]=='get_topic_alert'):
                """ http://127.0.0.1:8081/get_topic_alert?house=house1&device=gas"""
                result = resource_manager.get_topic_alert(params['house'],params['device'])

            elif(uri[0]=='print_house'):
                """ - print_house (need to specify as a parameter the name of the new house):returns all the data related
                      to that house in the resource catalog

                       house = requests.get("http://127.0.0.1:8080/print_house?house_id=house1").json()  """
                param=params['house_id']
                result = resource_manager.print_house(param)
            elif(uri[0]=='print_all'):
                """ - print_all_resources (no other param needed):returns all the resource catalog
                       printall = requests.get("http://127.0.0.1:8080/print_all").json()"""
                result = resource_manager.print_all()
            elif(uri[0]=='save_all'):
                """ - save_all_resources (no other param needed):saves the changes
                       N.B when you modify something using one of the functions written in the following lines
                       they automatically call save_all_resources, so there's no need to save the changes separately.
                       The function return a message saying that everything is ok, otherwise an error message

                       save = requests.get("http://127.0.0.1:8080/save_all").json()  """
                result =resource_manager.save_all()
            elif(uri[0]=='add_house'):
                """ - add_house (need to specify as a parameter the NAME of the new house and room) :
                       the parameters you are giving will be used by the code to build the actual IDENTIFIER. the code will then
                       check the uniqueness of the id, add the specified house with a room and automatically save the changes

                       add_house = requests.get("http://127.0.0.1:8080/add_house?house_id=house6").json()  """
                param = params['house_id']
                check = resource_manager.unique(param,'kitchen',0)
                if check =='ok':
                    result =resource_manager.add_house(param)
                    resource_manager.save_all()
                else:
                    result = check
            elif(uri[0]=='delete_house'):
                """ - delete_room (need to specify as a parameter the name of the room to delete):
                       deletes the specified house and automatically saves the changes

                       delete_house = requests.get("http://127.0.0.1:8080/delete_house?house_id=house6").json()  """
                param = params['house_id']
                result =resource_manager.delete_house(param)
                resource_manager.save_all()
            elif(uri[0]=='add_room'):
                """ - add_room (need to specify as a parameter the NAME of the house where you want to add it and the NAME of the new room) :
                      the parameters you are giving will be used by the code to build the actual IDENTIFIER. the code will then
                       check the uniqueness of the id, add the new room to the specified house and automatically save the changes

                       add_room = requests.get("http://127.0.0.1:8080/add_room?house_id=house1&room_id=room9").json()  """
                param = params['house_id']
                param1 = params['room_id']
                check = resource_manager.unique(param,param1,1)
                if check =='ok':
                    result =resource_manager.add_room(param,param1)
                    resource_manager.save_all()
                else:
                    result = check
            elif(uri[0]=='delete_room'):
                """ - delete_room (need to specify as a parameter the IDENTIFIER of the room to delete):
                      deletes the room from the specified house and automatically saves the changes

                       delete_room = requests.get("http://127.0.0.1:8080/delete_room?room_id=house1_room9").json() """
                param = params['room_id']
                result =resource_manager.delete_room(param)
                resource_manager.save_all()
            elif(uri[0]=='switch_status'):
                """ - turn_on_off (requires as a parameter the IDENTIFIER and the new status [ON/OFF]):
                           this function can change the status of a device from OFF (dispositivo spento) to ON (dispositivo acceso)
                           and it automatically saves the changes.
                           there a 4 options:
                            0- you pass as a parameter an empty string and status: in exceptional cases can be used to shut on/off everything, otherwise it does nothing
                            1- you pass as a parameter only the id of the house and status: all the devices of the house will have the new status
                            2- you pass as a parameter the id of a room and status: all the devices of the room will have the new status
                            3- you pass as a parameter the id of a device and status: that specific device will have the new status

                           on_off = requests.get("http://127.0.0.1:8080/switch_status?id=house1_room1_camera&status=ON").json() """
                identifier = params["id"]
                value = params["status"]
                result =resource_manager.switch_status(identifier,value)
                resource_manager.save_all()
            elif(uri[0]=='get_chw'):
                """ get thingspeak ch write Apikey  and field """
                device=params['id']
                result = resource_manager.get_chw(device)
            elif(uri[0]=='get_chr'):
                """ get thingspeak ch read  """
                device=params['id']
                result = resource_manager.get_chr(device)

            elif(uri[0] == "get_houses"):
                result = resource_manager.get_houses()

            elif(uri[0] == "get_rooms"):
                house_id = params["house_id"]
                result = resource_manager.get_rooms(house_id)

            elif(uri[0] == "get_status"):
                device_id = params["id"]
                result = resource_manager.get_status(device_id)

            elif(uri[0] == "chat_house"):
                chatid = params["id"]
                result = resource_manager.chat_house(chatid)

            elif(uri[0] == "house_chat"):
                houseid = params["id"]
                result = resource_manager.house_chat(houseid)
                
            elif(uri[0] == 'get_address'):
                result = resource_manager.get_address()
                
            elif(uri[0] == 'get_threshold'):
                result = resource_manager.get_threshold(params["device_id"])
                
            elif(uri[0] == "change_threshold"):
                identifier = params["id"]
                value = int(params['value'])
                result = resource_manager.house_chat(identifier,value)
                resource_manager.save_all()
            return result

        except:
            return json.dumps("Ooops! there was an error")




if __name__ == '__main__':
    config_file = 'configuration.json'
    config=open(config_file,'r')
    configuration=config.read()
    config.close()
    config=json.loads(configuration)
    res_file = "ResourceCatalogue.json"
    res_op = open(res_file,'r')
    res = res_op.read()
    res_op.close()
    resource = json.loads(res)
    
    cherrypy.config.update({'server.socket_host': resource['ip']})
    cherrypy.config.update({'server.socket_port': resource['port']})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            # 'tools.session.on': True,
            }
        }    
    cherrypy.tree.mount(CatalogueWebService(),'/', conf)
    cherrypy.engine.start()
    
    
    
    service_address = config['servicecat_address']
    request_address = service_address+'update_service?id='+resource['catalogue_id']+'&ip='+resource['ip']+'&port='+str(resource['port'])
    #resource_address = "http://"+res_address["ip"]+ ":"+str(res_address["port"])
    #print(request_address)
    
        
    
    try:
        update = requests.get(request_address).json()
        print(update)
    except:
        print('Error in contacting Service Catalog')
    
    
    cherrypy.engine.block()

        # netstat -ano | findstr :PORTA
        # taskkill /PID PROCESSID /F
