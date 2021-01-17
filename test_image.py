# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

name = "Thi"  # replace with your name
img_counter = 0
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)
# allow the camera to warmup
time.sleep(0.1)
# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array
# display the image on screen and wait for a keypress
img_name = "dataset/" + name + "/image_{}.jpg".format(img_counter)
cv2.imwrite(img_name, image)
cv2.imshow("Image", image)
cv2.waitKey(0)
