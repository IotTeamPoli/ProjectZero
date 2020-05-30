import requests
from PIL import Image
import telegram
import json
import os
TOKEN = "801308577:AAFpc5w-nzYD1oHiY-cj_fJVaKH92P4uLCI"
bot = telegram.Bot(token=TOKEN)

camera_ip = "127.0.0.1"
camera_port: 8082
i = 0
saving_path = 'temp_saving/'
if not os.path.exists(saving_path):
    os.makedirs(saving_path)

import numpy as np

#res = requests.get("http://127.0.0.1:8082/take_picture").json() # fai una foto. ritorna array
# foto_list = res['msg']# è una lista, va convertira in array
# print(type(foto_list))
# i = 0
# for foto in foto_list:
#     array_ = np.asarray(foto, np.uint8)
#     image = Image.fromarray(array_, 'RGB')  #  PIL image
#     image.save(saving_path+str(i)+'.jpg')
#     #image.show()
#     with open(saving_path+str(i)+'.jpg', 'rb') as f:
#         print('hey')
#         bot.send_photo(chat_id='557427612', photo=f)  # manda solo un'immagine in memoria
#     i += 1



res = requests.get("http://127.0.0.1:8082/get_history").json() # dammi tutte le foto in memoria. titorna lista di path per ogni immagine
#res = requests.get("http://127.0.0.1:8082/get_photo_day?year=2020&month=05&day=24").json()  # dammi le foto fatte in un giorno, ritorna lista di foto in un giorno

# TODO: per gli STORICI: res ritorna: return json.dumps({"msg": msg}) e msg può essere meddaggio 'no foto' o la lista delle foto
#   quindi telegram deve  fare un check sul tipo di msf che riceve : if (type(res['msg'])) is list: send foto
#   else: send mesage

i = 0
dict_ = dict(res)
for k,v in dict_.items():
    print(k)
    array_ = np.asarray(v, np.uint8)
    image = Image.fromarray(array_, 'RGB')  #  PIL image
    image.save(saving_path+array_)
    #image.show()
    with open(saving_path+array_, 'rb') as f:
        bot.send_photo(chat_id='557427612', photo=f)  # manda solo un'immagine in memoria
    i += 1



#res = requests.delete("http://127.0.0.1:8082/delete_all").json() # cancella tutte le foto in memoria; ritorna un msg con 'ok' o 'niente da cancellare'
#res = requests.delete("http://127.0.0.1:8082/delete_day?year=2020&month=05&day=24").json() # cancella tutte le foto di un giorno; rotorna 'ok' o 'niente da cancellare'
# TODO: res ritorna json.dumps({"msg": msg}) e msg è una stringa




# img_path = res["path"]
# print(img_path)
# if type(img_path)
# for image in img_path:
#     with Image.open(image) as img:
#         img.show() # qui c'è img show, in telegram andrà:


# TODO: per le prove ho usato img.show. Per telegram bisogna mettere bot.send_photo
#  ma bisogna provare cosa preferisce per aprirle: uno dei due metodi:


# per telegram sarà:
# c'è da capire se invece va cambiato con:
#for image in img_path:
#     with Image.open(image) as img:
#         bot.send_photo(chat_id='128817114', photo=f)

# oppure con:
#for image in img_path:
#   with open(imgage, 'rb') as img:
#       bot.send_photo(chat_id='128817114', photo=img)

