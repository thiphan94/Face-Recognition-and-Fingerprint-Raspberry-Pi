import cv2
import numpy as np
import os
import time
import board
from time import sleep
from datetime import datetime
import pyrebase
from picamera.array import PiRGBArray
import picamera
from picamera import PiCamera
import requests
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

import RPi.GPIO as GPIO

import serial
from datetime import date

today = date.today()

uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=10)


finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

config = {
    "apiKey": "AIzaSyDPy-_F290OjEOpKQgtt9F1JtGk76tFaRU",
    "authDomain": "rpi-security-ee0c0.firebaseapp.com",
    "databaseURL": "https://rpi-security-ee0c0-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "rpi-security-ee0c0",
    "storageBucket": "rpi-security-ee0c0.appspot.com",
    "messagingSenderId": "391814499821",
    "appId": "1:391814499821:web:b892ff4e18ad36c4acabe4",
    "measurementId": "G-66JBD9P1H6",
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

relay = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, GPIO.LOW)

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT


# function for setting up emails
def send_message(id):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxd71d1f5272f54ccd9fa926d5554b5a02.mailgun.org/messages",
        auth=("api", "21f1a75d40a6aba32a504e4f749d36a5-1553bd45-5afa17a2"),
        # files=[("attachment", (name, open("name", "rb").read()))],
        data={
            "from": "hello@example.com",
            "to": ["thiphan94@gmail.com"],
            "subject": "You have a visitor",
            "html": "<html>" + str(id) + " is at your door.  </html>",
        },
    )


# function for getting fingerprint


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image of fingerprint...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


##################################################


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/trainer.yml")
cascadePath = "Detection/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX
# iniciate id counter
id = 0
# names related to ids: example ==> Marcelo: id=1,  etc
names = ["None", "Thi"]
# Initialize and start realtime video capture
cam = cv2.VideoCapture(-1)
cam.set(3, 640)  # set video widht
cam.set(4, 480)  # set video height
# Define min window size to be recognized as a face
minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)
while True:
    ret, img = cam.read()

    if ret == False:
        break
        # end of movie
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )
    now = datetime.now()

    # dt = now.strftime("%d%m%Y%H:%M:%S")
    dt = now.strftime("%d%m%Y")
    temps = now.strftime("%H:%M:%S")

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y : y + h, x : x + w])
        # Check if confidence is less them 100 ==> "0" is perfect match
        # time.sleep(2)
        if confidence < 100:
            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
            print(id)

            cam.release()
            cv2.destroyAllWindows()
            time.sleep(2)
            print("Fingerprint----------------")

            if get_fingerprint():
                print(
                    "door lock Detected #",
                    finger.finger_id,
                    "with confidence",
                    finger.confidence,
                )

                data = {"name": str(id), "date": str(dt), "time": str(temps)}
                db.child("users").push(data)
                GPIO.output(relay, 1)
                # print(LOCK DOOR)
            else:
                id = "unknown"
                print("Finger not found, unlock")
                GPIO.output(relay, 0)
                data = {"name": str(id), "date": str(dt), "time": str(temps)}
                db.child("users").push(data)

                request = send_message(id)
                print(
                    "Status Code: " + format(request.status_code)
                )  # 200 status code means email sent successfully

        else:

            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))

        cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

    cv2.imshow("camera", img)
    k = cv2.waitKey(10) & 0xFF  # Press 'ESC' for exiting video
    if k == 27:
        break
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
