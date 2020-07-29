# Programming for IoT Application Project
Project developed in the "Programming for IoT applications" course at Politecnico di Torino, "ICT for Smart Societies" Master Degree.
# Authors
- [Lorenzo Bellone](https://github.com/LorenzoBellone)
- [Silvia Bennici](https://github.com/SilviaPboli)
- [Giulia Ciaramella](https://github.com/GiuliaCiaramella)
- [Matteo Zhang](https://github.com/MatteoZhang)

# Videos
- [Video Demo](https://www.youtube.com/watch?v=bLeYA_SulaA&feature=youtu.be)
- [Video Promo](https://www.youtube.com/watch?v=FTmHMn-HqOM)

# IoT For Home Security
The proposed platform integrates different IoT devices and technologies that allow the remote monitoring of a house. The owner will feel secure while he is not at home thanks to the detection of undesired people through bluetooth sniffers and the sensing of unexpected movements together with photos triggered by these movements.
Moreover, there are other metrics that the platform will be able to monitor such as humidity, temperature and gas.
Our platform follows the microservice design pattern. 
The catalogs contain information of the system stored in json format.
## Service catalog 
(Catalog Folder)  
It contains information about how to reach the main services of our system, like the broker, the resource catalog, the presence catalog and the “camera servers”.
## Resource catalog 
(Catalog Folder)  
Here we can acquire information about all the registered houses, the rooms and the devices that are present in each of them. It provides these information to other services of the system.
## Presence Catalog 
(Catalog Folder)  
Here we have information about bluetooth beacons that are detected in all the houses, which can be associated with unknown, allowed or unwanted people.
All the catalogs communicate via REST Web Services with all the other actors of the system. All the services that connect to the service catalog will register and perform a registration update with given intervals. If the update does not arrive on time, the service is unregistered from the catalog.
## Device Connectors
(Mqtt_and_Sensors Folder)  
Represent the lowest level of the application. The Raspberry Pi and an Arduino have been connected to the used sensors and actuators (temperature, humidity, bluetooth sniffer and cameras for the raspberry, gas for the arduino). All the sensors are mqtt publishers that send their values under a given topic. The camera, instead, is a web server that will return a photo only when a certain request arrives from the motion control strategy.
## Control Strategies
(Control Folder)  
are meant to provide essential alerts for user awareness. The gas strategy is a simple mqtt subscriber and publisher which takes the values sent from the gas sensors and compares them with a threshold. Whenever the current gas value is too high, an alert is sent to the broker with a given topic. 
The motion strategy detects movements inside the house when no one is supposed to be there and sends an alert together with a photo in correspondence of the detected movement. The photo is requested to the camera server via http protocol. Finally, the presence control is the strategy to fill the presence catalog. It receives information from the bluetooth sniffers and properly adds this information to the presence catalog, specifying who this person is (unknown, accepted or unwanted) and whether this person is present.
## ThingSpeak and Freeboard 
(Mqtt_and_Sensors Folder and Client Folder)  
In order to give visual feedback to the user, a data visualization service can be implemented thanks to the use of thingspeak together with freeboard. The sensor data sent by the broker via mqtt are collected by the thingspeak adaptor, and sent via REST service to the channels provided by thingspeak. Thingspeak allows a very fine data representation thanks to its graphs and widgets. Each house will have its own channel and all the sensors know which is the field to fill. The graphs give information over time about temperature, humidity and gas.  The Freeboard provides a more user friendly visualization thanks to a dashboard. It acquires data through rest service from thingspeak and, for each user, shows graphs and widgets on temperature, humidity and gas sensed. 
## Telegram Bot 
(Client Folder)  
The telegram bot provides a system interface for the users. A user is associated with one or more houses according to its chat identificator. If the chat id of the user does not correspond with any house, this person cannot receive information and alerts. The telegram bot allows the user to perform many different commands and to receive alerts in a fast and clear way. In any moment we can have information about the current temperature and humidity in the rooms of our house, information about the gas sensed in the kitchen and the bluetooth transmitters that are detected at the very moment. The alerts that the user receives regard the gas value (the threshold can be directly changed by the user himself), unexpected movements when the user is not at home followed by a photo, and detected blacklisted people that are in the house.
The user can set the status for the motion and bluetooth alerts, in order to switch them on or off.
