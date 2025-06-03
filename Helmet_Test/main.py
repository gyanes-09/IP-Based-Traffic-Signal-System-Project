import json
from ultralytics import YOLO
import cv2
import numpy as np
from sort.sort import *
from util import get_car, read_license_plate
import torch

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load criminal vehicle numbers from a CSV file
def load_criminal_plates(file_path):
    criminal_plates = set()
    with open(file_path, 'r') as file:
        for row in file:
            criminal_plates.add(row.strip())
    return criminal_plates

def detect_vehicles():
    results = {}
    mot_tracker = Sort()

    # Load models
    coco_model = YOLO('yolov8n.pt').to(device)
    license_plate_detector = YOLO('./models/license_plate_detector.pt').to(device)

    # Load video
    cap = cv2.VideoCapture('./sample.mp4')

    # Define vehicle classes (COCO IDs)
    vehicles = [2, 3, 5, 7]

    # Load criminal plates
    criminal_plates = load_criminal_plates('/Users/suryanshkhatri/Documents/autoTest/criminal_plates.csv')

    frame_nmr = -1
    ret = True
    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if ret:
            results[frame_nmr] = {}

            # Detect vehicles
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])

            # Track vehicles
            track_ids = mot_tracker.update(np.asarray(detections_))

            # Detect license plates
            license_plates = license_plate_detector(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate

                # Assign license plate to car
                xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

                if car_id != -1:
                    # Crop and process license plate
                    license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]
                    license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                    _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)
                    license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                    if license_plate_text is not None:
                        results[frame_nmr][car_id] = {
                            'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                            'license_plate': {
                                'bbox': [x1, y1, x2, y2],
                                'text': license_plate_text,
                                'bbox_score': score,
                                'text_score': license_plate_text_score
                            }
                        }

                        # Check for criminal plates
                        if license_plate_text in criminal_plates:
                            print(f"Alert: Criminal vehicle detected - {license_plate_text}")

    cap.release()
    return results  # Return JSON-ready dictionary
