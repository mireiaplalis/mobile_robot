from picarx import Picarx
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance

def main():
    try:
        px = Picarx()
        with PiCamera() as camera:
            camera.resolution = (160, 128)  
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            found_object = False
            for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True): # use_video_port=True
                img = frame.array
                dist = distance(img)
                print("Distance", dist)
                if dist is not None:
                    found_object = True
                
                if dist is None:
                    if found_object:
                        break
                    px.forward(0.22)
                    time.sleep(0.5)
                    px.forward(0)
                elif dist > 25:
                    px.forward(0.22)
                    time.sleep(1)
                    px.forward(0)
                elif dist > 15:
                    px.forward(0.22)
                    time.sleep(0.3)
                    px.forward(0)
                elif dist > 5:
                    px.forward(0.22)
                    time.sleep(0.1)
                    px.forward(0)
                else:
                    break
                
                rawCapture.truncate(0)
    finally:
        px.forward(0)

if __name__=="__main__":
    main()
