# !/usr/bin/env python3

import time

import cv2
import numpy as np
import psutil
from PIL import Image

classes = None

excluded_ids = [0, 56, 60, 13, 57]
# person, chair, dining table, bench, couch

with open('yolov3.txt', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))


def focal_length_finder():
    # distance from camera to object in cm
    reference_object_distance = 14.7

    # Real width of the reference object
    reference_object_real_width = 9.7  

    # object width(pixels) in the reference_image
    ref_object_width = 80

    # finding the focal length
    focal_length = (ref_object_width * reference_object_distance) / reference_object_real_width
    return focal_length


FOCAL_LENGTH = focal_length_finder()


def distance_finder(focal_length, real_width, width_in_frame):
    """
    Distance estimation function
    """
    distance = (real_width * focal_length) / width_in_frame

    return distance


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

    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def distance(img, show=False):
    focal_length = FOCAL_LENGTH

    # Real width of the object we're trying to detect
    target_object_real_width = 7  

    cfg = 'yolov3.cfg'
    weights = 'yolov3.weights'
    scale = 0.009

    net = cv2.dnn.readNet(weights, cfg)

    img_width = img.shape[1]
    img_height = img.shape[0]
    blob = cv2.dnn.blobFromImage(img, scale, (img.shape[0], img.shape[1]), (0, 0), True, crop=False)
    net.setInput(blob)
    start = time.time()
    outs = net.forward(get_output_layers(net))
    print("Forward time: ", time.time() - start)

    # Hide image
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4
    # For each detection from each output layer
    # get the confidence, class id, bounding box params
    # and ignore weak detections (confidence < 0.5)
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * img_width)
                center_y = int(detection[1] * img_height)
                w = int(detection[2] * img_width)
                h = int(detection[3] * img_height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([center_x, center_y, x, y, w, h])

    # Apply non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # Go through the detections remaining after nms and draw bounding box
    for i in indices:
        i = i[0]
        box = boxes[i]
        center_x = box[0]
        center_y = box[1]
        x = box[2]
        y = box[3]
        w = box[4]
        h = box[5]

        distance = distance_finder(focal_length, target_object_real_width, w)
        if show:
            draw_prediction(img, class_ids[i], confidences[i], round(x), 
                            round(y), round(x + w), round(y + h))
        if class_ids[i] not in excluded_ids:
            if show:
                pil = Image.fromarray(np.uint8(img))
                pil.show()
            return distance, center_x, center_y
        
    if show:
        pil = Image.fromarray(np.uint8(img))
        pil.show()
    return None, None, None

