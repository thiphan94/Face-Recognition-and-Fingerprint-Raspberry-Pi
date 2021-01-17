import io
import picamera
import cv2
import numpy

# Create a memory stream so photos doesn't need to be saved in a file
stream = io.BytesIO()

# Get the picture (low resolution, so it should be quite fast)
# Here you can also specify other parameters (e.g.:rotate the image)
with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.capture(stream, format="jpeg")

# Convert the picture into a numpy array
buff = numpy.frombuffer(stream.getvalue(), dtype=numpy.uint8)

# Now creates an OpenCV image
image = cv2.imdecode(buff, 1)

# https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
# Load a cascade file for detecting faces
face_cascade = cv2.CascadeClassifier(
    "/home/pi/Face Recognition/haarcascade_frontalface_default.xml"
)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Look for faces in the image using the loaded cascade file
faces = face_cascade.detectMultiScale(gray, 1.1, 5)

print("Found {}" + str(len(faces)) + " face(s)")

# Draw a rectangle around every found face
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 4)

# Save the result image
cv2.imwrite("result.jpg", image)
