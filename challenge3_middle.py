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
    time.sleep(0.3)
    camera.capture(stream, format='jpeg')
    #time.sleep(0.5)
    stream.seek(0)
    img = Image.open(stream)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def look_and_turn(px, camera, side):
    import pdb; pdb.set_trace()
    px.set_camera_servo1_angle(side * 90)
    img = take_picture(camera)
    dist, x, y = distance(img, show=True)
    if dist is not None:
        turn_in_place(px, side)
        #turn_right(px, 1.6 + (x_right - 80) * 0.007, turn_angle)
    px.set_camera_servo1_angle(0)
    return dist is not None

def turn_right(px, turn_time, turn_angle):
    px.set_dir_servo_angle(turn_angle)
    px.forward(0.22)
    time.sleep(turn_time)
    px.forward(0)
    px.set_dir_servo_angle(0)
    return

def turn_in_place(px, side=1):
    px.forward(-0.22)
    time.sleep(0.5)
    px.set_dir_servo_angle(side * 30)
    px.forward(0.22)
    time.sleep(1.4)
    px.set_dir_servo_angle(0)
    px.forward(-0.22)
    time.sleep(0.5)
    px.forward(0)
    return

def main():
    turn_angle = 30
    step_time = 1.5
    total_line_steps = 4
    line_steps_remaining = 2
    turns = 0
    sides = [1, -1, -1, -1, -1, -1, 1, 1]
    look = ["right", "both", "left", "left", "left", "both", "right", "right"]
    # count number of turns towards each
    # direction while object not found
    index = 0
    # direction 1 = right
    direction = -1
    try:
        px = Picarx()
        with PiCamera() as camera:
            camera.resolution = (160, 128)  
            camera.start_preview()
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            found_object = False
            prev_dist = 100
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
                    px.set_dir_servo_angle(-turn_angle)
                    px.forward(20)
                    time.sleep(0.1)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                elif x is not None and x > 90:
                    px.set_dir_servo_angle(turn_angle)
                    px.forward(20)
                    time.sleep(0.1)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                else:    
                    if dist is None:
                        if found_object and prev_dist < 15:
                            px.forward(0.22)
                            time.sleep(0.2)
                            px.forward(0)
                            break
                        else:
                            found_object = False
                            # Searching
                            if line_steps_remaining == 0:
                                # Turning 90 degrees right
                                print("Turning")
                                if turns > 7:
                                    break
                                turn_in_place(px, sides[turns])
                                if turns % 2 == 0:
                                    line_steps_remaining = total_line_steps
                                else:
                                    line_steps_remaining = total_line_steps / 2
                                turns += 1
                            else:
                                px.forward(0.22)
                                time.sleep(step_time)
                                px.forward(0)
                                line_steps_remaining -= 1
                            found = False
                            print(look[turns])
                            if look[turns] == "right" or look[turns] == "both":
                                found = look_and_turn(px, camera, 1)
                            if look[turns] == "left" or (look[turns] == "both" and not found):
                                look_and_turn(px, camera, -1)
                            
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

if __name__ == "__main__":
    main()




