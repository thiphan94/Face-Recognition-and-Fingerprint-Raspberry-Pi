from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import RPi.GPIO as GPIO
import numpy as np
import os
import board
from time import sleep
from datetime import datetime
import pyrebase
from picamera.array import PiRGBArray
import picamera
from picamera import PiCamera
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

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

RELAY = 17
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY, GPIO.OUT)
GPIO.output(RELAY, GPIO.LOW)

# Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
# Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"
# use this xml file
# https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
cascade = "Detection/haarcascade_frontalface_default.xml"


def send():

    time.sleep(1)
    camera = picamera.PiCamera()
    camera.resolution = (800, 600)
    camera.start_preview()
    time.sleep(5)
    now = datetime.now()
    dt = now.strftime("%d%m%Y%H:%M:%S")
    name = dt + ".jpg"
    camera.capture(name, resize=(640, 480))
    camera.stop_preview()
    storage.child(name).put(name)
    print("Image sent")
    os.remove(name)
    print("File Removed")
    # camera.close()


# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
# vs = VideoStream(src=-1).start()
# # vs = VideoStream(usePiCamera=True).start()
# time.sleep(2.0)
#
# start the FPS counter
fps = FPS().start()

prevTime = 0
doorUnlock = False

cam = cv2.VideoCapture(-1)
cam.set(3, 640)  # set video widht
cam.set(4, 480)  # set video height
# Define min window size to be recognized as a face
minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)


# loop over imgs from the video file stream
while True:

    ret, img = cam.read()

    if ret == False:
        break
        # end of movie
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    rects = detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(int(minW), int(minH)),
    )

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"  # if face is not recognized, then print Unknown

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # to unlock the door
            GPIO.output(RELAY, GPIO.HIGH)
            prevTime = time.time()
            doorUnlock = True
            print("door unlock")

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)

            # If someone in your dataset is identified, print their name on the screen
            if currentname != name:
                currentname = name
                print(currentname)

            send()
            # loop over the recognized faces

        # update the list of names
        names.append(name)

        # lock the door after 5 seconds
    if doorUnlock == True and time.time() - prevTime > 5:
        doorUnlock = False
        GPIO.output(RELAY, GPIO.LOW)
        print("door lock")
        #
        # time.sleep(1)
        # camera = picamera.PiCamera()
        # camera.resolution = (800, 600)
        # camera.start_preview()
        # time.sleep(5)
        # now = datetime.now()
        # dt = now.strftime("%d%m%Y%H:%M:%S")
        # name = dt + ".jpg"
        # camera.capture(name, resize=(640, 480))
        # camera.stop_preview()
        # storage.child(name).put(name)
        # print("Image sent")
        # os.remove(name)
        # print("File Removed")
    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image - color is in BGR
        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(img, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # display the image to our screen
    cv2.imshow("Facial Recognition is Running", img)
    key = cv2.waitKey(1) & 0xFF

    # quit when 'q' key is pressed
    if key == 27:
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
