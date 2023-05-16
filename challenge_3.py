from picarx import Picarx
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from distancer import distance
from Helper import take_picture, move_forward, look_and_turn, turn, turn_in_place



def main():
    turn_angle = 30
    # Forward time to do a step
    step_time = 1.8
    # Number of steps in before changing direction
    total_line_steps = 3
    line_steps_remaining = 4 # The first side is longer
    turns = 0
    try:
        px = Picarx()
        with PiCamera() as camera:
            # Camera configuration
            camera.resolution = (320, 256)  
            camera.start_preview()
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            # Whether the robot has found the object at any previous time
            found_object = False
            prev_dist = np.inf

            # We try to recognize the object rotating the camera to the right
            # If we find the object we turn towards it
            look_and_turn(px, camera, 1)
            while True:
                img = take_picture(camera)
                dist, x, y = distance(img, show=True)

                print("Distance", dist)
                
                # Object has been recognized in the image
                if dist is not None:
                    found_object = True
                    prev_dist = dist
                
                middle = camera.resolution[0] / 2
                margin = 10 if middle < 100 else 20

                # If object in the left of the image move left
                if x is not None and x < middle - margin:
                    px.set_dir_servo_angle(-turn_angle)
                    move_forward(px, 0.15)
                    px.set_dir_servo_angle(0)
                # If object in the right of the image move right
                elif x is not None and x > middle + margin:
                    px.set_dir_servo_angle(turn_angle)
                    move_forward(px, 0.15)
                    px.set_dir_servo_angle(0)
                else:    
                    if dist is None:
                        # We are too close to the object and we 
                        # stop recognizing it -> slightly forward and stop
                        if found_object and prev_dist < 15:
                            move_forward(px, 0.25)
                            break
                        else:
                            found_object = False
                            # Searching
                            # The robot completed one side of trajectory -> turn
                            if line_steps_remaining == 0:
                                if turns > 3:
                                    # We finished trajectory with no success
                                    break
                                turn(px, 2.0, turn_angle, 1)
                                # Start new side
                                line_steps_remaining = total_line_steps
                                turns += 1
                            else:
                                # Perform a step
                                move_forward(px, step_time)
                                line_steps_remaining -= 1
                            found = False
                            # Look right and if not found look left. 
                            # If found turn towards object
                            found = look_and_turn(px, camera, 1)
                            if not found:
                                look_and_turn(px, camera, -1)
                            
                    # The closer we are, the smaller the step
                    elif dist > 35:
                        camera.resolution = (320, 256)
                        move_forward(px, 0.7)
                    elif dist > 20:
                        # Decrease resolution if we are closer
                        camera.resolution = (160, 128)
                        move_forward(px, 0.6)
                    elif dist > 5:
                        camera.resolution = (160, 128)
                        move_forward(px, 0.2)
                    # If we are very close stop
                    else:
                        break
                rawCapture.truncate(0)
    finally:
       px.forward(0)

if __name__ == "__main__":
    main()





