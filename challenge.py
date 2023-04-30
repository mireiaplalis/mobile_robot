from picarx import Picarx
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance
import cv2

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
            for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=False): # use_video_port=True
                img = frame.array
                dist, x, y = distance(img, show=True)

                print("Distance", dist)
                print("x: ", x)
                print("y: ", y)
                if dist is not None:
                    found_object = True
                
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
                        if found_object:
                            px.forward(0.22)
                            time.sleep(0.1)
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
