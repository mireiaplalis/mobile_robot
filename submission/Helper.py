import cv2
from io import BytesIO
from PIL import Image
import numpy as np
import time
from distancer import distance

def take_picture(camera):
    """
    Stops for 0.5s and takes a steady picture
    """
    stream = BytesIO()
    time.sleep(0.5)
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    img = Image.open(stream)
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img

def move_forward(px, time_moving, speed=0.2):
    px.forward(speed)
    time.sleep(time_moving)
    px.forward(0)

def look_and_turn(px, camera, side):
    """
    Moves camera, and takes picture.
    If the object is recognized the robot turns 
    in place towards it.
    """
    px.set_camera_servo1_angle(side * 90)
    img = take_picture(camera)
    dist_s, x, y = distance(img, show=True)
    turn_time = 1.7 if side == 1 else 0.6
    if dist_s is not None:
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
    """
    Moves backward, turns and move backward
    again to turn in place.
    """
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