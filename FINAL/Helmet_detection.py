import torch
import cv2
import easyocr
import numpy as np
from ultralytics import YOLO
import argparse

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load YOLO models
bike_detector = YOLO('yolov8n.pt').to(device)  # Generic object detection
helmet_detector = YOLO('helmet_detection.pt').to(device)  # Pretrained helmet detection model
license_plate_detector = YOLO('license_plate_detector.pt').to(device)

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=True)

def detect_helmet(frame):
    results = helmet_detector(frame)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            label = "Helmet" if class_id == 0 else "No Helmet"
            
            color = (0, 255, 0) if class_id == 0 else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return frame

def detect_license_plate(frame):
    results = license_plate_detector(frame)
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            license_plate_crop = frame[y1:y2, x1:x2]
            detections = reader.readtext(license_plate_crop)
            
            for detection in detections:
                bbox, text, score = detection
                text = text.upper().replace(' ', '')
                if len(text) > 4:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, text, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    return text
    return None

def process_frame(frame):
    frame = detect_helmet(frame)
    plate_number = detect_license_plate(frame)
    if plate_number:
        print(f"License Plate: {plate_number}")
    return frame

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, default=None, help='IP address of the camera')
    args = parser.parse_args()
    
    # Use IP camera or default webcam
    source = f'http://{args.ip}:8080/video' if args.ip else 0
    cap = cv2.VideoCapture(source)
    
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = process_frame(frame)
        cv2.imshow("Helmet & License Plate Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
