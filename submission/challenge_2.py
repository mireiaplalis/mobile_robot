from picarx import Picarx
import time
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance
from Helper import take_picture, move_forward


def main():
    right_angle = 30
    left_angle = -30
    try:
        px = Picarx()
        finished = False
        # Counts how much time we have gone forward
        forward_time = 0
        # Total forward time to move 200cm
        total_time = 3.95
        with PiCamera() as camera:
            # Camera configuration
            camera.resolution = (160, 128)  
            camera.framerate = 24
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            # Whether the robot has found the object at any previous time
            found_object = False
            while not finished:
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
                    forward_time += 0.05
                    px.set_dir_servo_angle(0)
                # If object in the right of the image move right
                elif x is not None and x > middle + margin:
                    px.set_dir_servo_angle(right_angle)
                    move_forward(px, 0.1)
                    forward_time += 0.05
                    px.set_dir_servo_angle(0)
                # If object in front move forward
                else:    
                    # If object hasn't been recognized yet
                    if dist is None and (not found_object or prev_dist > 15):
                        move_forward(px, 0.5)
                        forward_time += 0.5
                    # If we are sill far from object go forward
                    elif dist is not None and dist > 26:
                        move_forward(px, 0.4)
                        forward_time += 0.4
                    # If we are close to object we avoid it and finish the 200cm
                    else:
                        print("starting turn")
                        px.set_dir_servo_angle(right_angle)
                        move_forward(px, 0.7)
                        px.set_dir_servo_angle(left_angle)
                        move_forward(px, 1.4)
                        px.set_dir_servo_angle(right_angle)
                        move_forward(px, 0.7)
                        px.set_dir_servo_angle(0)
                        time.sleep(total_time-forward_time)
                        finished = True
                        break

                rawCapture.truncate(0)
    finally:
        px.forward(0)

if __name__=="__main__":
    main()

