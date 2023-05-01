# !/usr/bin/env python3

import time

import cv2
import numpy as np
import psutil
from PIL import Image
#from ultralytics import YOLO

classes = None

with open('yolov3.txt', 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
#yolov8 = YOLO("yolov8n.pt")  # load a pretrained YOLOv8n model


def focal_length_finder():
    # distance from camera to object measured
    # centimeter
    reference_object_distance = 14.7

    reference_object_real_width = 9.7  # Real width of the reference object

    # reading reference_image from directory
    ref_image = cv2.imread("ref.jpg")

    # find the object width(pixels) in the reference_image
    ref_object_width = 80

    # finding the focal length
    focal_length = (ref_object_width * reference_object_distance) / reference_object_real_width
    return focal_length


FOCAL_LENGTH = focal_length_finder()


# distance estimation function
def distance_finder(focal_length, real_width, width_in_frame):
    distance = (real_width * focal_length) / width_in_frame

    # return the distance
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
    # get the focal by calling "Focal_Length_Finder"
    # face width in reference(pixels),
    # Known_distance(centimeters),
    # known_width(centimeters)
    focal_length = FOCAL_LENGTH
    print(focal_length)

    target_object_real_width = 9.7  # Real width of the object we're trying to detect

    cfg = 'yolov3.cfg'
    weights = 'yolov3.weights'
    scale = 0.009

    net = cv2.dnn.readNet(weights, cfg)

    cv2.imwrite('ref.jpg', img)
    Width = img.shape[1]
    Height = img.shape[0]
    blob = cv2.dnn.blobFromImage(img, scale, (img.shape[0], img.shape[1]), (0, 0), True, crop=False)
    net.setInput(blob)
    start = time.time()
    outs = net.forward(get_output_layers(net))
    print("Forward time: ", time.time() - start)

    # hide image
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()
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
                boxes.append([center_x, center_y, x, y, w, h])

            # apply non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # go through the detections remaining
    # after nms and draw bounding box
    for i in indices:
        i = i[0]
        box = boxes[i]
        center_x = box[0]
        center_y = box[1]
        x = box[2]
        y = box[3]
        w = box[4]
        h = box[5]
        print('box', x, y, w, h)
        # finding the distance by calling function
        # Distance finder function need
        # these arguments the Focal_Length,
        # Known_width(centimeters),
        # and Known_distance(centimeters)

        distance = distance_finder(
            focal_length, target_object_real_width, w)
        print('Distance', distance)
        if show:
            try:
                draw_prediction(img, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))
            except:
                import pdb;
                pdb.set_trace()
            pil = Image.fromarray(np.uint8(img))
            pil.show()
        if class_ids[i] == 41:
            return distance, center_x, center_y
        else:
            return None, None, None
    if show:
        pil = Image.fromarray(np.uint8(img))
        pil.show()
    return None, None, None

'''
def distance_v8(image):
    target_object_real_width = 9.7
    start = time.time()
    result = yolov8.predict(image)  # predict on an image
    print("v8 Prediction took", time.time() - start, "seconds")

    plot = result[0].plot()
    cv2.imshow("Box", plot)

    best_conf = 0
    dist = None
    x, y = None, None
    # Return the distance to the box with the highest confidence.
    for i, b in enumerate(result[0].boxes.xywh):
        w = b[2]
        conf = result[0].boxes.conf[i]
        if conf > best_conf:
            best_conf = conf
            dist = distance_finder(FOCAL_LENGTH, target_object_real_width, w)
            x, y = b[0], b[1]

    return dist.item(), x.item(), y.item()
'''
