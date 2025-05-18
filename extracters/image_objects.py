from ultralytics import YOLO
import cv2
from utils.dd import dd

def resize_with_letterbox(image, target_size=640):
    h, w = image.shape[:2]
    scale = min(target_size / w, target_size / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Compute padding
    pad_w = target_size - new_w
    pad_h = target_size - new_h
    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left

    padded = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
    return padded

def image_objects(image_path):
    model = YOLO("yolo11n.pt")
    img = cv2.imread(image_path)
    img_resized = resize_with_letterbox(img, target_size=640)
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
    results = model(img_rgb)
    object_names = set()
    for r in results:
        for c in r.boxes.cls:
            object_names.add(model.names[int(c)])
    return list(object_names)