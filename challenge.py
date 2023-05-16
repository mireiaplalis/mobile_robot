from picarx import Picarx
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance
import cv2
from io import BytesIO
from PIL import Image

def take_picture(camera):
    stream = BytesIO()
    time.sleep(0.5)
    camera.capture(stream, format='jpeg')
    #time.sleep(0.5)
    stream.seek(0)
    img = Image.open(stream)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def main():
    right_angle = 20
    left_angle = -20
    try:
        px = Picarx()
        with PiCamera() as camera:
            camera.resolution = (160, 128)  
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            found_object = False
            while True:
                img = take_picture(camera)
                dist, x, y = distance(img, show=True)

                print("Distance", dist)
                print("x: ", x)
                print("y: ", y)
                if dist is not None:
                    found_object = True
                    prev_dist = dist

                if x is not None and x < 70:
                    px.set_dir_servo_angle(left_angle)
                    px.forward(20)
                    time.sleep(0.1)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                elif x is not None and x > 90:
                    px.set_dir_servo_angle(right_angle)
                    px.forward(20)
                    time.sleep(0.1)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                else:    
                    if dist is None:
                        if found_object and prev_dist < 15:
                            px.forward(0.22)
                            time.sleep(0.15)
                            px.forward(0)
                            break
                        px.forward(0.22)
                        time.sleep(0.5)
                        px.forward(0)
                    elif dist > 35:
                        px.forward(0.22)
                        time.sleep(0.8)
                        px.forward(0)
                    elif dist > 15:
                        px.forward(0.22)
                        time.sleep(0.3)
                        px.forward(0)
                    elif dist > 5:
                        px.forward(0.22)
                        time.sleep(0.2)
                        px.forward(0)
                    else:
                        break
                
                rawCapture.truncate(0)
    finally:
        px.forward(0)

if __name__=="__main__":
    main()
