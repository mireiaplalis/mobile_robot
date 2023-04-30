from picarx import Picarx
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance
import cv2

def main():
    right_angle = 30
    left_angle = -30
    try:
        px = Picarx()
        finished = False
        forward_time = 0
        total_time = 3.95
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
                    forward_time += 0.05
                    time.sleep(0.1)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                elif x is not None and x > 90:
                    px.set_dir_servo_angle(right_angle)
                    px.forward(20)
                    forward_time += 0.05
                    time.sleep(0.1)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                else:    
                    if dist is None and not found_object:
                        px.forward(0.2)
                        time.sleep(0.5)
                        forward_time += 0.5
                        px.forward(0)
                    elif dist is not None and dist > 20:
                        px.forward(0.2)
                        time.sleep(0.4)
                        forward_time += 0.4
                        px.forward(0)
                    else:
                        print("starting turn")
                        px.set_dir_servo_angle(right_angle)
                        px.forward(20)
                        time.sleep(0.7)
                        px.set_dir_servo_angle(left_angle)
                        time.sleep(1.3)
                        px.set_dir_servo_angle(right_angle)
                        time.sleep(0.75)
                        px.set_dir_servo_angle(0)
                        time.sleep(total_time-forward_time)
                        finished = True
                        break

                rawCapture.truncate(0)
                if finished:
                    break
    finally:
        px.forward(0)

if __name__=="__main__":
    main()

