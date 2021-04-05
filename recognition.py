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


# import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

import RPi.GPIO as GPIO


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


relay = 18
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, GPIO.LOW)

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT


# import serial
#
# uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=10)
#
#
# finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

##################################################


def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="", flush=True)
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="", flush=True)
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="", flush=True)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...", end="", flush=True)
        else:
            print("Place same finger again...", end="", flush=True)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="", flush=True)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="", flush=True)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True


##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter ID # from 1-127: "))
        except ValueError:
            pass
    return i


###########################################################


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer/trainer.yml")
cascadePath = "Detection/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)
font = cv2.FONT_HERSHEY_SIMPLEX
# iniciate id counter
id = 0
# names related to ids: example ==> Marcelo: id=1,  etc
names = ["None", "Thi", "Paula", "Ilza", "Z", "W"]
# Initialize and start realtime video capture
cam = cv2.VideoCapture(-1)
cam.set(3, 640)  # set video widht
cam.set(4, 480)  # set video height
# Define min window size to be recognized as a face
minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)
while True:
    ret, img = cam.read()

    # img = cv2.flip(img, -1)  # Flip vertically
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
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y : y + h, x : x + w])
        # Check if confidence is less them 100 ==> "0" is perfect match
        if confidence < 70:

            id = names[id]
            confidence = "  {0}%".format(round(100 - confidence))
            # confidence = "  {0}%".format(round(confidence))
            print(id)
            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(
                img, str(confidence), (x + 5, y + h - 5), font, 1, (0, 255, 0), 1
            )

            # time.sleep(5)
            #
            # cam.release()
            # cv2.destroyAllWindows()
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

            cam.release()
            cv2.destroyAllWindows()
            print("----------------")

            if get_fingerprint():
                print(
                    "door lock Detected #",
                    finger.finger_id,
                    "with confidence",
                    finger.confidence,
                )
                GPIO.output(relay, 1)
                # print(LOCK DOOR)
            else:
                print("Finger not found, unlock")
                GPIO.output(relay, 0)

            time.sleep(5)

            # cam.release()
            # cv2.destroyAllWindows()
            # time.sleep(1)
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

        else:
            id = "unknown"
            confidence = "  {0}%".format(round(100 - confidence))
            # confidence = "  {0}%".format(round(confidence))
            cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(
                img, str(confidence), (x + 5, y + h - 5), font, 1, (0, 255, 0), 1
            )

        # cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
        # cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

    cv2.imshow("camera", img)
    k = cv2.waitKey(10) & 0xFF  # Press 'ESC' for exiting video
    if k == 27:
        break
# Do a bit of cleanup
print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()
