import cv2
import picamera
import picamera.array


name = "Thi"  # replace with your name

img_counter = 0
with picamera.PiCamera() as camera:
    with picamera.array.PiRGBArray(camera) as stream:
        camera.resolution = (320, 240)

        while True:
            camera.capture(stream, "bgr", use_video_port=True)
            image = stream.array
            img_name = "dataset/" + name + "/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, image)
            # stream.array now contains the image data in BGR order
            cv2.imshow("frame", stream.array)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            # reset the stream before the next capture
            stream.seek(0)
            stream.truncate()

        cv2.destroyAllWindows()
