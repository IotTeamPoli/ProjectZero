from PIL import Image
import time
import json
from imutils.video import WebcamVideoStream
import io
import numpy as np
from imutils import opencv2matplotlib
camera = WebcamVideoStream(src=0).start()


def byte_array_to_pil_image(byte_array):
    return Image.open(io.BytesIO(byte_array))

time.sleep(5)

frame = camera.read()
print(np.shape(frame))
now = time.time()
room = 'ciao'

#np_array_RGB = opencv2matplotlib(frame)
image = Image.fromarray(frame, 'RGB')
image.save('prova1.jpg')
np_listed = frame.tolist()
message = {"array": np_listed, "time": now, "room": room}
message_json = json.dumps(message)


# recreate image
msg = json.loads(message_json)
array_ = np.asarray(msg["array"], np.uint8)
print(np.shape(array_))
#array_rgb = opencv2matplotlib(array_)
image = Image.fromarray(array_, mode='RGB')
image.save('prova2.jpg')
