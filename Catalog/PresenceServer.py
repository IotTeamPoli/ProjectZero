"""
author: Matteo Zhang
MyPresenceManager contain all the methods and the Server
"""
import cherrypy
import time
import json
import requests

FILENAME = "configuration.json"
CATALOG = "PresenceCatalogue.json"

# static read form file
with open(FILENAME, "r") as f:
    d = json.load(f)
    DEFAULT_ADDRESS = d["default_address"]
    SERVICE_ADDRESS = d["servicecat_address"]

with open(CATALOG, "r") as f:
    d = json.load(f)
    CATALOG_ID = d["catalogue_id"]
    PRESENCE_IP = d["ip"]
    PRESENCE_PORT = d["port"]


class MyPresenceManager(object):
    """
    docstring for MyPresenceManager.
    http://localhost:8081/URI?PARAMS
    -- all prints and gets just need URI[0]
    es:
    http://localhost:8081/print_all_whitelist
    http://localhost:8081/get_tot
    -- all add methods needs params
    params must be initialized it's ok even if it contains null
        "home": null,
        "mac": null,
        "name": null,
        "surname": null,
        "device_name": null,
        "present": null,
        "last_detected": null
    es:
    http://localhost:8081/add_to_white?PARAMS
    """

    def __init__(self):
        self.filename = CATALOG
        with open(self.filename, "r") as file:
            self.data = json.load(file)

    def print_all_whitelist(self):
        """print all whitelist people
        http://localhost:8081/print_all_whitelist
        """
        return self.data["white_list"]

    def print_all_blacklist(self):
        """print all backlist people
        http://localhost:8081/print_all_blacklist
        """
        return self.data["black_list"]

    def print_all_unknown(self):
        """print all unknown people
        http://localhost:8081/print_all_unknown
        """
        return self.data["unknown"]

    def get_tot(self):
        """return tot number of recorded device
        http://localhost:8081/get_tot
        """
        return self.data["tot"]

    def get_tot_present(self):
        """return tot number of present people
        http://localhost:8081/get_tot_present
        """
        return self.data["tot_present"]

    def get_all_records(self):
        """return all records in the presence catalog
        http://localhost:8081/get_all_records
        """
        records = []
        for i in self.data["white_list"]:
            records.append(i)
        for i in self.data["black_list"]:
            records.append(i)
        for i in self.data["unknown"]:
            records.append(i)
        return records

    def get_all_inside(self):
        """return all people inside the house
        http://localhost:8081/get_all_inside
        """
        inside = []
        for i in self.data["white_list"]:
            if i["present"] == 1:
                inside.append(i)
        for i in self.data["black_list"]:
            if i["present"] == 1:
                inside.append(i)
        for i in self.data["unknown"]:
            if i["present"] == 1:
                inside.append(i)
        return inside

    def add_to_white(self, params):
        """add a person to white list
        http://localhost:8081/add_to_white
        """
        try:
            with open(self.filename, "w") as out:
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                flag = 0
                for i in self.data["white_list"]:
                    if i["name"] == params["name"] and i["surname"] == params["surname"] and i["mac"] == params["mac"]:
                        flag = 1
                if flag:
                    print("entry already present!!!\n")
                else:
                    self.data["last_update"] = now
                    self.data["white_list"].append(params)
                self.data["tot"] = len(self.data["white_list"] + self.data["unknown"] + self.data["black_list"])
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)

    def add_to_black(self, params):
        """add a person to black list
        http://localhost:8081/add_to_black
        """
        try:
            with open(self.filename, "w") as out:
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                flag = 0
                for i in self.data["black_list"]:
                    if i["name"] == params["name"] and i["surname"] == params["surname"] and i["mac"] == params["mac"]:
                        flag = 1
                if flag:
                    print("entry already present!!!\n")
                else:
                    self.data["last_update"] = now
                    self.data["black_list"].append(params)
                self.data["tot"] = len(self.data["white_list"] + self.data["unknown"] + self.data["black_list"])
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)

    def add_to_unknown(self, params):
        """add a person to unknown
        http://localhost:8081/add_to_unknown
        """
        try:
            with open(self.filename, "w") as out:
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                flag = 0
                for i in self.data["unknown"]:
                    if i["name"] == params["name"] and i["surname"] == params["surname"] and i["mac"] == params["mac"]:
                        flag = 1
                if flag:
                    print("entry already present!!!\n")
                else:
                    self.data["last_update"] = now
                    self.data["unknown"].append(params)
                self.data["tot"] = len(self.data["white_list"] + self.data["unknown"] + self.data["black_list"])
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)

    def count_present(self):
        """count the presence field
        http://localhost:8081/count_present
        """
        tot_present = 0
        try:
            with open(self.filename, 'w') as out:
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                for i in self.data["unknown"]:
                    if i["present"] == 1:
                        tot_present += 1
                for i in self.data["black_list"]:
                    if i["present"] == 1:
                        tot_present += 1
                for i in self.data["white_list"]:
                    if i["present"] == 1:
                        tot_present += 1
                self.data["tot_present"] = tot_present
                self.data["last_update"] = now
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)

    def rmv_this_person(self, params):
        """remove a specific person specified in params
        this method uses only the mac parameter
        http://localhost:8081/rmv_this_person
        """
        try:
            with open(self.filename, "w") as out:
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                found = 0
                for i in self.data["white_list"]:
                    if i["mac"] == params["mac"]:
                        found = 1
                        self.data["white_list"].remove(i)
                for i in self.data["black_list"]:
                    if i["mac"] == params["mac"]:
                        found = 1
                        self.data["black_list"].remove(i)
                for i in self.data["unknown"]:
                    if i["mac"] == params["mac"]:
                        found = 1
                        self.data["unknown"].remove(i)
                if found:
                    self.data["last_update"] = now
                    print("person removed")
                else:
                    print("not found")
                self.data["tot"] = len(self.data["white_list"] + self.data["unknown"] + self.data["black_list"])
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)

    def rmv_all(self):
        """remove every entry
        http://localhost:8081/rmv_all
        """
        try:
            with open(self.filename, "w") as out:
                self.data["white_list"].clear()
                self.data["black_list"].clear()
                self.data["unknown"].clear()
                self.data["tot"] = len(self.data["white_list"] + self.data["unknown"] + self.data["black_list"])
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)

    def update_time(self):
        """update time
        http://localhost:8081/update_time
        """
        try:
            with open(self.filename, "w") as out:
                named_tuple = time.localtime()  # get structured_time
                now = time.strftime("%d/%m/%Y, %H:%M:%S", named_tuple)
                self.data["last_update"] = now
                json.dump(self.data, out, indent=4)
        except Exception as e:
            print("exception: ", e)


class MyServer(object):
    """docstring for MyServer."""
    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        operation = MyPresenceManager()
        print("uri: ", uri, "params: ", params)
        try:
            if uri[0] == "print_all_whitelist":
                data = operation.print_all_whitelist()
            elif uri[0] == "print_all_blacklist":
                data = operation.print_all_blacklist()
            elif uri[0] == "print_all_unknown":
                data = operation.print_all_unknown()
            elif uri[0] == "get_tot":
                data = operation.get_tot()
            elif uri[0] == "get_tot_present":
                data = operation.get_tot_present()
            elif uri[0] == "get_all_records":
                data = operation.get_all_records()
            elif uri[0] == "get_all_inside":
                data = operation.get_all_inside()
            return data
        except Exception as e:
            print(e)
            return e

    def PUT(self, *uri, **params):
        # modify something for es: if we want to change the presence field just remove and add.
        print("uri: ", uri, "params: ", params)
        operation = MyPresenceManager()
        try:
            if uri[0] == "update_time":
                operation.update_time()
            elif uri[0] == "add_to_white":
                operation.add_to_white(params)
                operation.count_present()
                operation.update_time()
            elif uri[0] == "add_to_black":
                operation.add_to_black(params)
                operation.count_present()
                operation.update_time()
            elif uri[0] == "add_to_unknown":
                operation.add_to_unknown(params)
                operation.count_present()
                operation.update_time()
            elif uri[0] == "rmv_this_person":
                operation.rmv_this_person(params)
                operation.count_present()
                operation.update_time()
        except Exception as e:
            print(e)
            return e

    def DELETE(self, *uri, **params):
        print("uri: ", uri, "params: ", params)
        operation = MyPresenceManager()
        try:
            if uri[0] == "rmv_all":
                operation.rmv_all()
                operation.count_present()
                operation.update_time()
        except Exception as e:
            print(e)
            return e


def registration(address, catalog_id, ip, port):
    """register to service catalog"""
    try:
        url = address + "update_service?id=" + catalog_id + "&ip=" + ip + "&port=" + str(port)
        res = requests.get(url)
        print("status: ", res.status_code)
    except Exception as e:
        print("failed: ", e)


def main():
    registration(SERVICE_ADDRESS, CATALOG_ID, PRESENCE_IP, PRESENCE_PORT)
    cherrypy.config.update({'server.socket_host': DEFAULT_ADDRESS})
    cherrypy.config.update({'server.socket_port': PRESENCE_PORT})
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(MyServer(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
