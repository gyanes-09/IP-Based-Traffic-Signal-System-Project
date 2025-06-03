import cv2
import numpy as np
from ultralytics import YOLO
from time import time

# Load YOLOv8 model with tracking
model = YOLO('yolov8n.pt')  # Pre-trained model from Ultralytics

# Parameters
FPS = 30  # Adjust based on your video source
PIXELS_PER_METER = 10  # Calibration factor (needs real-world tuning)
MIN_CONFIDENCE = 0.5  # Minimum confidence for detections
SPEED_LIMIT = 60  # Speed limit in km/h
LANE_BOUNDARY_X = None  # Will be set to frame width / 2 by default

def calculate_speed(prev_position, curr_position, frame_time, pixels_per_meter):
    """Calculate speed in km/h based on pixel displacement."""
    distance_pixels = np.sqrt((curr_position[0] - prev_position[0])**2 + 
                             (curr_position[1] - prev_position[1])**2)
    distance_meters = distance_pixels / pixels_per_meter
    speed_mps = distance_meters / frame_time  # Speed in meters per second
    return speed_mps * 3.6  # Convert to km/h

def check_violations(center_x, speed, frame_width):
    """Check for speeding and lane crossing violations."""
    violations = []
    
    # Speeding violation
    if speed > SPEED_LIMIT:
        violations.append(f"Speeding: {speed:.1f} km/h (> {SPEED_LIMIT} km/h)")
    
    # Lane crossing violation (assuming center_x crossing LANE_BOUNDARY_X)
    if LANE_BOUNDARY_X is not None:
        if center_x < LANE_BOUNDARY_X - 50 or center_x > LANE_BOUNDARY_X + 50:  # Buffer zone
            violations.append("Lane Crossing")
    
    return violations

def process_video(video_path):
    # Open video feed (use 0 for webcam, or provide a file path)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
  
    car_positions = {}
    frame_count = 0
    prev_time = time()

 
    ret, frame = cap.read()
    if ret:
        frame_height, frame_width = frame.shape[:2]
        global LANE_BOUNDARY_X
        LANE_BOUNDARY_X = frame_width // 2 
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        curr_time = time()
        frame_time = curr_time - prev_time if frame_count > 1 else 1/FPS

        # Perform object detection and tracking with YOLOv8
        results = model.track(frame, persist=True, classes=[2], conf=MIN_CONFIDENCE)  # Class 2 is 'car'
        
        # Draw lane boundary (for visualization)
        if LANE_BOUNDARY_X is not None:
            cv2.line(frame, (LANE_BOUNDARY_X, 0), (LANE_BOUNDARY_X, frame_height), (255, 0, 0), 2)

        # Process tracking results
        if results[0].boxes.id is not None:  # Check if tracking IDs are available
            boxes = results[0].boxes.xyxy.cpu().numpy()  # [x_min, y_min, x_max, y_max]
            track_ids = results[0].boxes.id.cpu().numpy()  # Tracking IDs
            confidences = results[0].boxes.conf.cpu().numpy()

            for box, track_id, conf in zip(boxes, track_ids, confidences):
                x_min, y_min, x_max, y_max = box
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                car_id = int(track_id)  # Use YOLOv8's tracking ID
                
                # Draw bounding box and ID
                cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {car_id}", (int(x_min), int(y_min) - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Calculate speed if we have a previous position
                speed = 0.0
                if car_id in car_positions and 'position' in car_positions[car_id]:
                    prev_pos = car_positions[car_id]['position']
                    speed = calculate_speed(prev_pos, (center_x, center_y), frame_time, PIXELS_PER_METER)
                    cv2.putText(frame, f"Speed: {speed:.1f} km/h", (int(x_min), int(y_min) - 25), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Check for violations
                violations = check_violations(center_x, speed, frame_width)
                for i, violation in enumerate(violations):
                    color = (0, 0, 255)  # Red for violations
                    cv2.putText(frame, violation, (int(x_min), int(y_min) - 10 - i*15), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Update car position and timestamp
                car_positions[car_id] = {'position': (center_x, center_y), 'time': curr_time}
        
        # Clean up old car entries (remove after 1 second of no detection)
        car_positions = {k: v for k, v in car_positions.items() if curr_time - v['time'] < 1.0}
        prev_time = curr_time

        # Display the frame
        cv2.imshow('Traffic Violation Detection', frame)
        
        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Replace with your video file path or use 0 for webcam
    video_path = "/Users/akashsaha/Desktop/traffic_system/sample.mp4"
    process_video(video_path)