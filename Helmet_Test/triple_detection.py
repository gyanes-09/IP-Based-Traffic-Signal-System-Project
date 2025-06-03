import torch
import cv2
import numpy as np
from ultralytics import YOLO

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load YOLO models
bike_detector = YOLO('yolov8n.pt').to(device)  # Generic object detection
person_detector = YOLO('yolov8n.pt').to(device)  # Detects persons

def detect_triple_riding(frame):
    bike_results = bike_detector(frame)
    person_results = person_detector(frame)
    
    bikes = []
    persons = []
    
    # Detect bikes
    for result in bike_results:
        for box in result.boxes:
            if int(box.cls[0]) == 3:  # Class 3 is usually for motorcycles
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bikes.append((x1, y1, x2, y2))
    
    # Detect persons
    for result in person_results:
        for box in result.boxes:
            if int(box.cls[0]) == 0:  # Class 0 is usually for persons
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                persons.append((x1, y1, x2, y2))
    
    violations = []
    
    for bx1, by1, bx2, by2 in bikes:
        count = 0
        for px1, py1, px2, py2 in persons:
            # Check if the person is within the bike's bounding box
            if bx1 < px1 < bx2 and by1 < py1 < by2:
                count += 1
        
        if count > 2:
            violations.append((bx1, by1, bx2, by2))
    
    # Draw boxes and labels
    for bx1, by1, bx2, by2 in violations:
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 0, 255), 2)
        cv2.putText(frame, "Triple Riding Detected", (bx1, by1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    return frame

def main():
    cap = cv2.VideoCapture(0)  # Replace with IP camera URL if needed
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = detect_triple_riding(frame)
        cv2.imshow("Triple Riding Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
