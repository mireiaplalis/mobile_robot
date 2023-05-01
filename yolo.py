import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # load a pretrained YOLOv8n model

image = cv2.imread("near.jpg")

x = model.predict(image)  # predict on an image

for r in x:
    print(f"Detected {len(x)} objects")
    for b in r.boxes.xyxy:
        box = b.cpu().numpy()
        print(box)
        start = int(box[0]), int(box[1])
        end = (int(box[2]), int(box[3]))
        print(start, end)
plot = x[0].plot()
cv2.imshow("Box", plot)
cv2.waitKey(0)
cv2.destroyAllWindows()
