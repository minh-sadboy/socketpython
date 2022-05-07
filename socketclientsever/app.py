from flask import Flask, render_template
from flask_socketio import SocketIO , emit
import cv2
import numpy as np
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key!'
socketio = SocketIO(app)

# base64 to img
def readb64(uri):
   encoded_data = uri.split(',')[1]
   nparr = np.fromstring(base64.b64decode(encoded_data), np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   return img

# img to base64
def encodeb64(uri):
    retval, buffer = cv2.imencode('.png', uri)
    jpg_as_text = base64.b64encode(buffer)
    result = str(jpg_as_text)
    return result 

def opencv(data):
    img = readb64(str(data))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lwr = np.array([80, 0, 0])
    upr = np.array([179, 255, 146])
    msk = cv2.inRange(hsv, lwr, upr)
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dlt = cv2.dilate(msk, krn, iterations=5)
    res = 255 - cv2.bitwise_and(dlt, msk)   
    result = encodeb64(res)
    return result

@app.route('/')
def html():
    return render_template('index.html')

# Receive a message from the front end HTLM
@socketio.on('send_message')   
def message_recieved(data):
    result = opencv(data['data'])
    emit('message_from_server', {'result': result})

# Actually Start the App
if __name__ == '__main__':
    """ Run the app. """    
    socketio.run(app, port=8000, debug=False)