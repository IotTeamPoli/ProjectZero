import json
from datetime import datetime
import copy
import time


class ResourceManager:
    def __init__(self):
        """When adding a new house or room, the code will retrieve the skeleton from 'ResourceCatalogueSkeleton.json'
        and then save the new house/room in 'ResourceCatalogue.json'"""
        self.skeleton_file = 'ResourceCatalogueSkeleton.json'
        skeleton = open(self.skeleton_file, 'r')
        ResourceSkeleton = skeleton.read()
        skeleton.close()
        self.skeleton = json.loads(ResourceSkeleton)

        self.res_file_name = 'ResourceCatalogue.json'
        resourcecat_file = open(self.res_file_name, 'r')
        ResourceCat = resourcecat_file.read()
        resourcecat_file.close()
        self.data = json.loads(ResourceCat)  # data is a dictionary

        self.last_update = self.data['last_update']
        # self.now = datetime.datetime.now()

    def unique(self, house_name, room_name, room_only):
        """checks the uniqueness of a new id:
            if room_only=1 the method checks if the id is already existing inside the given house (we are adding a room in a house)
            otherwise it checks the id of the house (we are adding a new house)"""
        flag = 0
        for house in self.data["house_list"]:
            if house["house_id"] == house_name and room_only == 0:
                flag = 1
                break
            elif house["house_id"] == house_name and room_only == 1:
                for room in house["room_list"]:
                    if room["room_id"] == house_name + '_' + room_name:
                        flag = 1
                        break
        if flag == 0:
            return 'OK'
        else:
            return json.dumps("Error : id already used, please choose another one")

    def get_topic(self, identifier="def:ault"):
        """given an id, it finds the corresponding mqtt topic
           there a 4 cases:
            0- you pass as a parameter an empty string :returns the topic of the entire catalog
            1- you pass as a parameter only the id of the house: returns the topic of the house
            2- you pass as a parameter the id of a room: returns the topic of the room
            3- you pass as a parameter the id of a device:returns the topic of the device
            4- you pass as a parameter "alert" :returns the alert topic   """

        tmp = identifier.split('_')
        length = len(tmp)  # between 0 and 3
        # house_name = tmp[0]
        # room_name=tmp[1]
        # device_name= tmp[2]
        if identifier == "ResourceCatalogue":  # here I'm not writing any Error message since the user shouldn't see all the catalog
            return json.dumps(self.data['topic'])
        elif identifier == "alert":
            return json.dumps(self.data['alert_topic'])
        elif length >= 1:
            for house in self.data['house_list']:
                if length == 1 and house['house_id'] == tmp[0]:
                    return json.dumps(house['topic'])
                elif length > 1 and house['house_id'] == tmp[0]:
                    for room in house['room_list']:
                        if length == 2 and room['room_id'] == tmp[0] + '_' + tmp[1]:
                            return json.dumps(room['topic'])
                        elif length >= 2 and room['room_id'] == tmp[0] + '_' + tmp[1]:
                            for device in room['device_list']:
                                if length == 3 and device['device_id'] == identifier:
                                    return json.dumps(device['topic'])
                                elif device == room['device_list'][-1]:
                                    return json.dumps("Error: device not found")
                        elif room == house['room_list'][-1]:
                            return json.dumps("Error : room not found")
                elif house == self.data['house_list'][-1]:
                    return json.dumps("Error : house not found")

    def get_topic_alert(self, house_id, device):
        ans = {}
        for house in self.data['house_list']:
            if house['house_id'] == house_id:
                top = "alert_topic_" + device
                ans["topic"] = house[top]
                return json.dumps(ans)
        if len(ans) == 0:
            ans = {house_id: "Error : house not found"}
            return json.dumps(ans)

    def print_house(self, house_name):
        """prints all the resources linked to that house"""
        ok = 0
        for house in self.data['house_list']:
            if house['house_id'] == house_name:
                ok = 1
                return json.dumps(house)
        if ok == 0:
            ans = {house_name: "Error : house not found"}
            return json.dumps(ans)

    def print_all(self):
        return json.dumps(self.data)

    def save_all(self):
        "the general last_update field is updated"""
        self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        out_file = open(self.res_file_name, 'w')
        out_file.write(json.dumps(self.data, indent=4))
        out_file.close()
        return json.dumps(self.data['last_update'], indent=4)

    def add_house(self, house_name):
        """the last_update of the house is created and updated"""
        new_house = copy.deepcopy(self.skeleton["house_list"][0])
        new_house["house_id"] = house_name
        new_house['topic'] = "ioteam/resourcecat/" + house_name
        new_house['alert_topic_gas'] = "ioteam/resourcecat/alert/" + house_name + "/alert_gas"
        new_house['alert_topic_motion'] = "ioteam/resourcecat/alert/" + house_name + "/alert_motion"
        new_house["ThingspeakChID"] = 7777
        new_house["ThingspeakAPIKeyW"] = 'apiwrite'
        new_house["ThingspeakAPIKeyR"] = 'apiread'
        room_name = new_house["room_list"][0]["room_id"]
        new_house["room_list"][0]["room_id"] = house_name + '_' + room_name
        new_house["room_list"][0]["topic"] = "ioteam/resourcecat/" + house_name + "/" + room_name

        count = 1
        for device in new_house["room_list"][0]["device_list"]:
            if device['device_name'] == 'camera' or device['device_name'] == 'motion' or device['device_name'] == 'bluetooth':
                pass
            else:
                device['ThingspeakField'] = count
                count += 1
            device["device_id"] = house_name + "_" + room_name + "_" + device["device_name"]
            device["topic"] = "ioteam/resourcecat/" + house_name + "/" + room_name + "/" + device["device_name"]
        new_house['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.data["house_list"].append(new_house)
        self.data["tot_house"] += 1
        return json.dumps("Ok : new house correctly added")

    def delete_house(self, house_name):
        count = 0
        flag = 0
        for house in self.data['house_list']:
            count += 1
            if house['house_id'] == house_name:
                # print('deleting: %r  %r' %(count,house_name))
                self.data['house_list'].pop(count - 1)
                flag = 1
                self.data['tot_house'] -= 1
                self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if flag == 1:
            return json.dumps('OK : house correctly deleted')
        else:
            return json.dumps('Error : no house with that name')

    def add_room(self, house_name, room_name):
        """in this case the last_update of the house is updated"""
        new_room = copy.deepcopy(self.skeleton["room_sample"][0])
        for house in self.data["house_list"]:
            if house["house_id"] == house_name:
                new_room["room_id"] = house_name + '_' + room_name
                new_room['topic'] = "ioteam/resourcecat/" + house_name + "/" + room_name
                if house['tot_room'] == 1:
                    count = 4
                else:
                    count = 4 + (house['tot_room'] - 1) * 2
                for device in new_room["device_list"]:
                    if device['device_name'] == 'camera' or device['device_name'] == 'motion' or device['device_name'] == 'bluetooth':
                        pass
                    else:
                        device['ThingspeakField'] = count
                        count += 1
                    device["device_id"] = house_name + "_" + room_name + "_" + device["device_name"]
                    device["topic"] = "ioteam/resourcecat/" + house_name + "/" + room_name + "/" + device["device_name"]
                house["room_list"].append(new_room)
                house["tot_room"] += 1
                house['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        return json.dumps("OK : new room correctly added")

    def delete_room(self, room_id):
        """in this case the last_update of the house is updated"""
        count = 0
        flag = 0
        tmp = room_id.split('_')
        for house in self.data['house_list']:
            if house['house_id'] == tmp[0]:
                for room in house['room_list']:
                    count += 1
                    if room['room_id'] == room_id:
                        # print('deleting: %r  %r' %(count,room_name))
                        house['room_list'].pop(count - 1)
                        flag = 1
                        house['tot_room'] -= 1
                        house['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if flag == 1:
            return json.dumps('OK : room correctly deleted')
        else:
            return json.dumps('Error : no room with that name')

    def switch_status(self, identifier='pressure', status="OFF"):
        # Set the status of a single or a group of devices
        """there a 4 cases:
            0- you pass as a parameter id='all' and status: case can be used to turn on/off everything
            1- you pass as a parameter only the id of the house and status: all the devices of the house will have the new status
            2- you pass as a parameter the id of a room and status: all the devices of the room will have the new status
            3- you pass as a parameter the id of a device and status: that specific device will have the new status"""

        tmp = identifier.split('_')
        flag = 0
        length = len(tmp)  # between 0 and 3
        # house_name = tmp[0]
        # room_name=tmp[1]
        # device_name= tmp[2]
        if length == 1 and tmp[0] == 'all':
            for house in self.data['house_list']:
                for room in house['room_list']:
                    for device in room['device_list']:
                        device['status'] = status
                        flag = 1

        elif length > 0 and tmp[0] != 'all':
            for house in self.data['house_list']:
                #print(tmp[0])
                if length >= 1 and house['house_id'] == tmp[0]:
                    for room in house['room_list']:
                        #print(room['room_id'])
                        if length == 1:
                            for device in room['device_list']:
                                device['status'] = status
                                flag = 1

                        elif length > 1 and room['room_id'] == tmp[0] + '_' + tmp[1]:
                            #print('ok loop')
                            for device in room['device_list']:
                                if length == 2:
                                    device['status'] = status
                                    flag = 1
                                elif length > 2 and device['device_id'] == identifier:
                                    device['status'] = status
                                    flag = 1
        if flag == 1:
            self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return json.dumps("OK : status updated")
        else:
            return json.dumps("Error : not found")

    def change_threshold(self, identifier='pressure', value=0):
        tmp = identifier.split('_')
        flag = 0
        for house in self.data['house_list']:
            if house['house_id'] == tmp[0]:
                for room in house['room_list']:
                    room_id = tmp[0] + '_' + tmp[1]
                    if room['room_id'] == room_id:
                        for device in room['device_list']:
                            if device['device_id'] == identifier:
                                device['threshold'] = value
                                flag = 1
        if flag == 1:
            self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return json.dumps("OK : threshold updated")
        elif flag != 1:
            return json.dumps("Error : device not found")

    def get_threshold(self, device_id):
        ans = {}
        tmp = device_id.split('_')
        room_id = tmp[0] + '_' + tmp[1]
        for house in self.data['house_list']:
            if house['house_id'] == tmp[0]:
                for room in house['room_list']:
                    if room['room_id'] == room_id:
                        for device in room['device_list']:
                            if device['device_id'] == device_id:
                                ans["threshold"] = device['threshold']

        if len(ans) != 0:
            return json.dumps(ans)
        elif len(ans) == 0:
            ans["threshold"] = -1
            return json.dumps(ans)

    def get_chw(self, device_id):
        # Returns the Thingspeak parameters to write a field
        ans = {}
        tmp = device_id.split('_')
        room_id = tmp[0] + '_' + tmp[1]
        for house in self.data['house_list']:
            if house['house_id'] == tmp[0]:
                ans["channel"] = house["ThingspeakChID"]
                ans["key"] = house["ThingspeakAPIKeyW"]
                for room in house['room_list']:
                    if room['room_id'] == room_id:
                        for device in room['device_list']:
                            if device['device_id'] == device_id:
                                ans["field"] = device['ThingspeakField']
        if len(ans) != 0:
            return json.dumps(ans)
        elif len(ans) == 0:
            ans["field"] = "Error : house not found"
            return json.dumps(ans)

    def get_chr(self, device_id):
        # Returns the Thingspeak parameters to read a field
        ans = {}
        tmp = device_id.split('_')
        room_id = tmp[0] + '_' + tmp[1]
        for house in self.data['house_list']:
            if house['house_id'] == tmp[0]:
                ans["channel"] = house["ThingspeakChID"]
                ans["key"] = house['ThingspeakAPIKeyR']
                for room in house['room_list']:
                    if room['room_id'] == room_id:
                        for device in room['device_list']:
                            if device['device_id'] == device_id:
                                ans["field"] = device['ThingspeakField']
        if len(ans) != 0:
            return json.dumps(ans)
        elif len(ans) == 0:
            ans["field"] = "Error : device not found"
            return json.dumps(ans)

    def get_houses(self):
        # Returns the list of the houses present in the resource catalog
        ans = {"houses": []}
        for house in self.data["house_list"]:
            ans["houses"].append(house["house_id"])
        return json.dumps(ans)

    def get_rooms(self, house_id=None):
        # returns the list of the rooms present in a house
        ans = {"rooms": []}
        for house in self.data["house_list"]:
            if house["house_id"] == house_id:
                for rooms in house["room_list"]:
                    ans["rooms"].append(rooms["room_id"])
        return json.dumps(ans)

    def get_status(self, device_id=None):
        # Given a unique device id returns its status
        ans = {}
        tmp = device_id.split('_')
        room_id = tmp[0] + '_' + tmp[1]
        for house in self.data['house_list']:
            if house['house_id'] == tmp[0]:
                for room in house['room_list']:
                    if room['room_id'] == room_id:
                        for device in room['device_list']:
                            if device['device_id'] == device_id:
                                ans["status"] = device["status"]
                                return json.dumps(ans)
        if len(ans) == 0:
            ans["status"] = "Error : device not found"
            return json.dumps(ans)

    def chat_house(self, chatid):
        # Given the chat id returns the house id
        ans = {"house": []}
        ok=0
        for house in self.data["house_list"]:
            if house["chatID"] == chatid:
                ok=1
                ans["house"].append(house["house_id"])
        # if ok==0:
        #     ans["house"].append("Error : house not found")
        return json.dumps(ans)

    def house_chat(self, houseid):
        # Given the house id returns the chat id
        ans = {}
        for house in self.data["house_list"]:
            if house["house_id"] == str(houseid):
                ans["chatID"] = house["chatID"]
                return json.dumps(ans)
        if len(ans) == 0:
            ans["chatID"] = "Error : device not found"
            return json.dumps(ans)

    def get_address(self):
        ans = {}
        ans['id'] = self.data['catalogue_id']
        ans['ip'] = self.data['ip']
        ans['port'] = self.data['port']
        # address = 'http://'+ip+':'+str(port)+'/'
        return json.dumps(ans)


class ServiceManager:
    def __init__(self):

        self.skeleton_file = 'ServiceCatalogueSkeleton.json'
        skeleton = open(self.skeleton_file, 'r')
        ServiceSkeleton = skeleton.read()
        skeleton.close()
        self.skeleton = json.loads(ServiceSkeleton)

        self.ser_file_name = 'ServiceCatalogue.json'
        servicecat_file = open(self.ser_file_name, 'r')
        ServiceCat = servicecat_file.read()
        servicecat_file.close()
        self.data = json.loads(ServiceCat)  # data is a dictionary

        self.last_update = self.data['last_update']

    def get_address(self, catid):
        ans = {}
        # print(catid)
        for cat in self.data['service_list']:
            if cat['id'] == catid:
                # print(cat['id'])
                ans['id'] = cat['id']
                ans['ip'] = cat['ip']
                ans['port'] = cat['port']
                # address = 'http://'+ip+':'+str(port)+'/'
                return json.dumps(ans)
        if len(ans) == 0:
            ans = {catid: "Error : Service not found"}
            return json.dumps(ans)

    def print_all_services(self):
        return json.dumps(self.data, indent=4)

    def update_service(self, service_name, ip, port):
        found = 0
        for service in self.data['service_list']:
            if (service["id"] == service_name):
                service['ip'] = ip
                service['port'] = port
                service['last_seen'] = time.time()
                found = 1
        if found == 1:
            return json.dumps('OK : service updated on service catalog')
        elif found == 0:
            new_service = copy.deepcopy(self.skeleton["service_list"][0])
            new_service['id'] = service_name
            new_service['port'] = port
            new_service['ip'] = ip
            new_service['last_seen'] = time.time()

            self.data['service_list'].append(new_service)
            self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return json.dumps('OK : new service added to service catalog')

    def get_ip(self, service_name):
        ok = 0
        for service in self.data['service_list']:
            if service['id'] == service_name:
                ok = 1
                return json.dumps(service['ip'])
        if ok == 0:
            return json.dumps('Error : service not found')

    def get_port(self, service_name):
        ok = 0
        for service in self.data['service_list']:
            if service['id'] == service_name:
                ok = 1
                return json.dumps(service['port'])
        if ok == 0:
            return json.dumps(-1)

    def get_lastseen(self, service_name):
        ok = 0
        for service in self.data['service_list']:
            if service['id'] == service_name:
                ok = 1
                return json.dumps(service['last_seen'])
        if ok == 0:
            return json.dumps(-1)

    def save_all(self):
        "Catalog is overwritten"""
        out_file = open(self.ser_file_name, 'w')
        out_file.write(json.dumps(self.data, indent=4))
        out_file.close()
        return json.dumps(self.data['last_update'], indent=4)

    def disconnect_service(self, service_name):
        """in this case the last_update is updated"""
        count = 0
        flag = 0
        for service in self.data['service_list']:
            count += 1
            if service['id'] == service_name:
                print('Request to disconnect %s' % (service_name))
                self.data['service_list'].pop(count - 1)
                flag = 1
                self.data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if flag == 1:
            return json.dumps('OK : service correctly disconnected')
        else:
            return json.dumps('Error : no service with that name')

    def get_broker(self):
        """IP address of the message broker"""
        ans = self.data["MqttBroker"]
        return json.dumps(ans)

    def get_broker_port(self):
        """port number of message broker"""
        ans = self.data["mqttport"]
        return json.dumps(ans)

# ------------------------------------------------------------------------------
# DEBUG
# ------------------------------------------------------------------------------

# if __name__=='__main__':
#     resource_manager=ResourceManager()
#    res = resource_manager.get_chw('house1_room1_gas')
#    res = resource_manager.unique('house1', 'room1',1)
#    res = resource_manager.get_topic('alert')
#    res = resource_manager.get_broker()
#    res = resource_manager.get_port()
#    res = resource_manager.save_all()
#     res = resource_manager.add_house("house1")
#     res = resource_manager.delete_house("house1")
#     res = resource_manager.add_room('house1', 'room2')
#     res = resource_manager.delete_room('house1_room2')
#     res = resource_manager.switch_status('all',"OFF")
#    res = resource_manager.change_threshold('house1_Kitchen_gas',20)
#    res = resource_manager.get_address()
#     save = resource_manager.save_all()
#    resources = resource_manager.print_all()
#    res = resource_manager.get_topic_alert('house1','motion')
#     res = resource_manager.print_house('house1')
#     print(res)

#     serv = ServiceManager()
#     ss = serv.disconnect_service('prova1')

#     s = serv.update_service('prova1','0.0.0.0',3333)
#    s = serv.get_ip('prova')
#     ss = serv.save_all()
