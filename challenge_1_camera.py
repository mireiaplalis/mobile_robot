#!/usr/bin/env python3

import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import numpy as np

def get_output_layers(net):
    
    layer_names = net.getLayerNames()
    try:
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    except:
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    label = str(classes[class_id])

    color = COLORS[class_id]

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

cfg = 'yolov3.cfg'
weights = 'yolov3.weights'
scale = 1

classes = None

with open('yolov3.txt', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

net = cv2.dnn.readNet(weights, cfg)

with PiCamera() as camera:
    camera.resolution = (160,128)  
    camera.framerate = 1
    rawCapture = PiRGBArray(camera, size=camera.resolution)  
    time.sleep(2)

    for frame in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True): # use_video_port=True
        img = frame.array
        Width = img.shape[1]
        Height = img.shape[0]
        blob = cv2.dnn.blobFromImage(img, scale, (img.shape[0], img.shape[1]), (0,0), True, crop=False)
        net.setInput(blob)
        start = time.time()
        outs = net.forward(get_output_layers(net))
        print("Forward time: ", time.time()-start)

        # initialization
        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        # for each detetion from each output layer 
        # get the confidence, class id, bounding box params
        # and ignore weak detections (confidence < 0.5)
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
            
                
                # apply non-max suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        # go through the detections remaining
        # after nms and draw bounding box
        print(indices)
        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            print('box', x, y, w, h)
            
            draw_prediction(img, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
        cv2.imshow("video", img)  # OpenCV image show
        #print('ids', indices)
        rawCapture.truncate(0)  # Release cache

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    print('quit ...') 
    cv2.destroyAllWindows()
