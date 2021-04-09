import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import pickle
import RPi.GPIO as GPIO
from time import sleep
from datetime import datetime
import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDJGdK9S9GWOQzpA8Vt0JnTuBQKPIX6G-w",
    "authDomain": "raspberry-image.firebaseapp.com",
    "databaseURL": "https://raspberry-image-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "raspberry-image",
    "storageBucket": "raspberry-image.appspot.com",
    "messagingSenderId": "69330911402",
    "appId": "1:69330911402:web:eddfee167d37422d6990d3",
    "measurementId": "G-LX4RCNF8Y5",
}

firebase = pyrebase.initialize_app(firebaseConfig)

storage = firebase.storage()

relay_pin = [26]
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, 0)

with open("labels", "rb") as f:
    dicti = pickle.load(f)
    f.close()

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))


faceCascade = cv2.CascadeClassifier("Detection/haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
    for (x, y, w, h) in faces:

        roiGray = gray[y : y + h, x : x + w]

        id_, conf = recognizer.predict(roiGray)

        for name, value in dicti.items():
            if value == id_:
                print(name)
            # break
            # print("out")
            if conf <= 70:
                # print("open")

                GPIO.output(relay_pin, 1)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    name + str(conf),
                    (x, y),
                    font,
                    2,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )
                # camera = picamera.PiCamera()
                # camera.resolution = (800, 600)
                # camera.start_preview()
                # sleep(5)
                # now = datetime.now()
                # dt = now.strftime("%d%m%Y%H:%M:%S")
                # name = dt + ".jpg"
                # camera.capture(name, resize=(640, 480))
                # camera.stop_preview()
                # storage.child(name).put(name)
                # print("Image sent")
                # os.remove(name)
                # print("File Removed")
                # # break

            else:
                GPIO.output(relay_pin, 0)
                # break

    cv2.imshow("frame", frame)
    key = cv2.waitKey(1)

    rawCapture.truncate(0)

    if key == 27:
        break

cv2.destroyAllWindows()
