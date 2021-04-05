from datetime import datetime
import time
import picamera
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
