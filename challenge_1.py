from picarx import Picarx
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance
from Helper import take_picture, move_forward


def main():
    right_angle = 20
    left_angle = -20
    try:
        px = Picarx()
        with PiCamera() as camera:
            # Camera configuration
            camera.resolution = (160, 128)  
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            # Whether the robot has found the object at any previous time
            found_object = False
            while True:
                img = take_picture(camera)
                dist, x, y = distance(img, show=True)

                print("Distance", dist)

                # Object has been recognized in the image
                if dist is not None:
                    found_object = True
                    prev_dist = dist

                middle = camera.resolution[0] / 2
                margin = 10
                # If object in the left of the image move left
                if x is not None and x < middle - margin:
                    px.set_dir_servo_angle(left_angle)
                    move_forward(px, 0.1)
                    px.set_dir_servo_angle(0)
                # If object in the right of the image move right
                elif x is not None and x > middle + margin:
                    px.set_dir_servo_angle(right_angle)
                    move_forward(px, 0.1)
                    px.set_dir_servo_angle(0)
                else:    
                    # If object hasn't been recognized
                    if dist is None:
                        # We are too close to the object and we 
                        # stop recognizing it -> slightly forward and stop
                        if found_object and prev_dist < 15:
                            move_forward(px, 0.15)
                            break
                        # We haven't recogized the object yet -> get closer
                        move_forward(px, 0.5)
                    # The closer we are, the smaller the step
                    elif dist > 35:
                        move_forward(px, 0.8)
                    elif dist > 15:
                        move_forward(px, 0.3)
                    elif dist > 5:
                        move_forward(px, 0.2)
                    # If we are super very stop
                    else:
                        break
                
                rawCapture.truncate(0)
    finally:
        # Stop
        px.forward(0)

if __name__=="__main__":
    main()
