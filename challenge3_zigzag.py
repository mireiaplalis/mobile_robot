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

'''
def look_and_turn(px, camera, side):
    angles = np.linspace(-45, 90, 2)
    images = []
    for angle in angles:
        px.set_camera_servo1_angle(angle)
        images.append(take_picture(camera))
    images = np.concatenate(images, axis=0)
    distances, xs, ys = distance(images, show=False)
    good_angle_idx = None
    min_dist = np.inf
    for i, d in enumerate(distances):
        if d is not None and d < min_dist:
            min_dist = d
            good_angle_idx = i
    
    turn_times = np.linspace(-0.6, 1.4, 5)
    if good_angle_idx is not None:
        print("should turn now")
        good_turn_time = turn_times(good_angle_idx)
        turn_in_place(px, np.abs(good_turn_time), np.sign(good_turn_time))
    px.set_camera_servo1_angle(0)
    return good_angle_idx is not None
'''

def look_and_turn(px, camera, side):
    px.set_camera_servo1_angle(side * 90)
    img = take_picture(camera)
    dist_s, x, y = distance(img, show=True)
    print("dist here", dist_s)
    turn_time = 1.7 if side == 1 else 0.6
    if dist_s is not None:
        print("should turn now")
        turn_in_place(px, turn_time, side)
    px.set_camera_servo1_angle(0)
    return dist_s is not None

def turn(px, turn_time, turn_angle, side):
    px.set_dir_servo_angle(turn_angle*side)
    px.forward(0.22)
    time.sleep(turn_time)
    px.forward(0)
    px.set_dir_servo_angle(0)
    return

def turn_in_place(px, turn_time, side=1):
    px.forward(-0.22)
    time.sleep(0.5)
    px.set_dir_servo_angle(side * 30)
    px.forward(0.22)
    time.sleep(turn_time)
    px.set_dir_servo_angle(0)
    px.forward(-0.22)
    time.sleep(0.5)
    px.forward(0)
    return

def main():
    turn_angle = 30
    step_time = 1.8
    total_line_steps = 3
    line_steps_remaining = 4
    turns = 0
    sides = [1, 1, 1, 1]
    look = ["both", "both", "both", "both", "both"]
    # count number of turns towards each
    # direction while object not found
    index = 0
    # direction 1 = right
    direction = -1
    try:
        px = Picarx()
        with PiCamera() as camera:
            camera.resolution = (320, 256)  
            camera.start_preview()
            rawCapture = PiRGBArray(camera, size=camera.resolution)  
            time.sleep(2)

            found_object = False
            prev_dist = 100
            look_and_turn(px, camera, 1)
            while True:
                img = take_picture(camera)

                dist, x, y = distance(img, show=True)
                print("Distance", dist)
                print("x: ", x)
                print("y: ", y)
                if dist is not None:
                    found_object = True
                    prev_dist = dist
                
                middle = camera.resolution[0] / 2

                margin = 10 if middle < 100 else 20

                if x is not None and x < middle - margin:
                    px.set_dir_servo_angle(-turn_angle)
                    px.forward(20)
                    time.sleep(0.15)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                elif x is not None and x > middle + margin:
                    px.set_dir_servo_angle(turn_angle)
                    px.forward(20)
                    time.sleep(0.15)
                    px.forward(0)
                    px.set_dir_servo_angle(0)
                else:    
                    if dist is None:
                        if found_object and prev_dist < 15:
                            px.forward(0.22)
                            time.sleep(0.25)
                            px.forward(0)
                            break
                        else:
                            found_object = False
                            # Searching
                            if line_steps_remaining == 0:
                                # Turning 90 degrees right
                                print("Turning")
                                if turns > 3:
                                    break
                                
                                turn(px, 2.2  - sides[turns] * 0.2, turn_angle, sides[turns])
                                line_steps_remaining = total_line_steps
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
                        camera.resolution = (320, 256)
                        px.forward(0.22)
                        time.sleep(0.7)
                        px.forward(0)
                    elif dist > 20:
                        camera.resolution = (160, 128)
                        px.forward(0.22)
                        time.sleep(0.6)
                        px.forward(0)
                    elif dist > 5:
                        camera.resolution = (160, 128)
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





