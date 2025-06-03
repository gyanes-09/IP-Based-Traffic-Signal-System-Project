import numpy as np
from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *
import os
import time
 
# Set up paths
video_path = "/Users/akashsaha/Desktop/traffic_system/ML_Project/data/test_videos/cars.mp4"
weights_path = "../Yolo-Weights/yolov8l.pt"
mask_path = "/Users/akashsaha/Desktop/traffic_system/ML_Project/data/images/mask.png"
graphics_path = "/Users/akashsaha/Desktop/traffic_system/ML_Project/graphics.png"

# Check file existence
if not os.path.exists(video_path):
    raise FileNotFoundError(f"Video file not found at {video_path}")
if not os.path.exists(weights_path):
    raise FileNotFoundError(f"YOLO weights file not found at {weights_path}")
if not os.path.exists(mask_path):
    raise FileNotFoundError(f"Mask image not found at {mask_path}")
if not os.path.exists(graphics_path):
    raise FileNotFoundError(f"Graphics image not found at {graphics_path}")

# Load video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Failed to open video file: {video_path}")

# Load YOLO model
model = YOLO(weights_path)

# Class names for YOLO
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter"]

# Load mask image
mask = cv2.imread(mask_path)
if mask is None:
    raise FileNotFoundError(f"Failed to load mask image from {mask_path}")

# Tracking setup
tracker = Sort(max_age=20, min_hits=3, iou_threshold=0.3)

# Define counting line
limits = [400, 297, 673, 297]
totalCount = set()
vehicle_counts = {'car': 0, 'truck': 0, 'bus': 0, 'motorbike': 0}
id_class_dict = {}

# Traffic light settings
traffic_light_phases = ['green', 'yellow', 'red']
current_phase_index = 0
phase_start_time = time.time()
vehicle_weights = {'car': 1, 'truck': 2, 'bus': 2, 'motorbike': 0.5}
min_green, max_green = 10, 60
yellow_duration = 3
green_duration = min_green
red_duration = green_duration + yellow_duration
phase_durations = {'green': green_duration, 'yellow': yellow_duration, 'red': red_duration}

while True:
    success, img = cap.read()
    if not success:
        print("Video ended or cannot read the frame.")
        break

    # Resize mask to match frame dimensions
    mask = cv2.resize(mask, (img.shape[1], img.shape[0]))
    imgRegion = cv2.bitwise_and(img, mask)

    # Overlay graphics
    imgGraphics = cv2.imread(graphics_path, cv2.IMREAD_UNCHANGED)
    if imgGraphics is not None:
        img = cvzone.overlayPNG(img, imgGraphics, (0, 0))
    else:
        print(f"Warning: Graphics image not loaded from {graphics_path}. Skipping overlay.")

    # YOLO detection
    results = model(imgRegion, stream=True)
    detections = np.empty((0, 5))
    detection_classes = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = math.ceil(box.conf[0].item() * 100) / 100
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass in vehicle_counts.keys() and conf > 0.3:
                detections = np.vstack([detections, [x1, y1, x2, y2, conf]])
                detection_classes.append(currentClass)

    # Update tracker
    resultsTracker = tracker.update(detections)

    # Map tracker IDs to their classes
    for result in resultsTracker:
        x1, y1, x2, y2, id = map(int, result)
        if id not in id_class_dict:
            # Assign the class of the first detection for this ID
            if len(detection_classes) > 0:
                id_class_dict[id] = detection_classes.pop(0)

    # Draw counting line
    cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 0, 255), 5)

    for result in resultsTracker:
        x1, y1, x2, y2, id = map(int, result)
        w, h = x2 - x1, y2 - y1
        cx, cy = x1 + w // 2, y1 + h // 2

        cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255))
        cvzone.putTextRect(img, f'ID: {id}', (max(0, x1), max(35, y1)), scale=2, thickness=3, offset=10)
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        if limits[0] < cx < limits[2] and limits[1] - 15 < cy < limits[1] + 15:
            if id not in totalCount:
                totalCount.add(id)
                class_name = id_class_dict.get(id, 'unknown')
                if class_name in vehicle_counts:
                    vehicle_counts[class_name] += 1
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 5)

    # Traffic light logic
    current_time = time.time()
    elapsed = current_time - phase_start_time
    current_phase = traffic_light_phases[current_phase_index]

    if elapsed >= phase_durations[current_phase]:
        current_phase_index = (current_phase_index + 1) % len(traffic_light_phases)
        phase_start_time = current_time

        if traffic_light_phases[current_phase_index] == 'green':
            total_weight = sum(vehicle_counts[vt] * vehicle_weights[vt] for vt in vehicle_counts)
            green_duration = min(max(min_green, total_weight * 2), max_green)
            phase_durations['green'] = green_duration
            phase_durations['red'] = green_duration + yellow_duration
            vehicle_counts = {vt: 0 for vt in vehicle_counts}

    # Draw traffic light
    light_positions = {'red': (50, 100), 'yellow': (50, 200), 'green': (50, 300)}
    for phase, (x, y) in light_positions.items():
        color = (0, 0, 255) if phase == 'red' else (0, 255, 255) if phase == 'yellow' else (0, 255, 0)
        if phase == current_phase:
            remaining_time = max(0, int(phase_durations[phase] - elapsed))
            cv2.circle(img, (x, y), 30, color, -1)
            cv2.putText(img, f'{phase}: {remaining_time}s', (x + 50, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            cv2.circle(img, (x, y), 30, (50, 50, 50), -1)

    # Display counts in real-time
    y_offset = 50
    for vt, count in vehicle_counts.items():
        cv2.putText(img, f'{vt}: {count}', (50, y_offset), cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 255), 5)
        y_offset += 50

    # Display total count
    cv2.putText(img, f'Total: {len(totalCount)}', (50, y_offset + 50), cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 255), 5)

    # Show frames
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()