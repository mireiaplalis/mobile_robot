import cv2

from distancer import distance_v8

image = cv2.imread("far.jpg")

print(distance_v8(image))
