# import RPi.GPIO as GPIO

# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
from datetime import datetime
import time
import picamera

# from time import sleep
import os

import cv2
import pyrebase

print("a")
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


print("b")
firebase = pyrebase.initialize_app(firebaseConfig)
print("c")
storage = firebase.storage()
print("d")
# camera = PiCamera()
print("e")
# while True:
#     try:
# if GPIO.input(10) == GPIO.HIGH:
camera = picamera.PiCamera()
camera.resolution = (800, 600)
camera.start_preview()
time.sleep(5)
camera.capture("snapshot.jpg", resize=(640, 480))
camera.stop_preview()
storage.child("snapshot.jpg").put("snapshot.jpg")
print("Image sent")
os.remove("snapshot.jpg")
print("File Removed")

# s = input()
# print(s)
# if s == "A":
#     print("pushed")
#     now = datetime.now()
#     dt = now.strftime("%d%m%Y%H:%M:%S")
#     name = dt + ".jpg"
#     camera.capture(name)
#     print(name + " saved")
#     storage.child(name).put(name)
#     print("Image sent")
#     os.remove(name)
#     print("File Removed")
# sleep(2)

# except:
#     camera.close()
