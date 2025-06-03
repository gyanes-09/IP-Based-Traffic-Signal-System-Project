import cv2
import numpy as np
from ultralytics import YOLO
from time import time


model = YOLO('yolov8n.pt')  


FPS = 30  
PIXELS_PER_METER = 10 
MIN_CONFIDENCE = 0.5  

def calculate_speed(prev_position, curr_position, frame_time, pixels_per_meter):
    """Calculate speed in km/h based on pixel displacement."""
    distance_pixels = np.sqrt((curr_position[0] - prev_position[0])**2 + 
                             (curr_position[1] - prev_position[1])**2)
    distance_meters = distance_pixels / pixels_per_meter
    speed_mps = distance_meters / frame_time  
    return speed_mps * 3.6  

def process_video(video_path):
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return
    
    
    car_positions = {}
    frame_count = 0
    prev_time = time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        curr_time = time()
        frame_time = curr_time - prev_time if frame_count > 1 else 1/FPS

        
        results = model.track(frame, persist=True, classes=[2], conf=MIN_CONFIDENCE)  # Class 2 is 'car'
        
        
        if results[0].boxes.id is not None:  
            boxes = results[0].boxes.xyxy.cpu().numpy()  
            track_ids = results[0].boxes.id.cpu().numpy()  
            confidences = results[0].boxes.conf.cpu().numpy()

            for box, track_id, conf in zip(boxes, track_ids, confidences):
                x_min, y_min, x_max, y_max = box
                center_x = (x_min + x_max) / 2
                center_y = (y_min + y_max) / 2
                car_id = int(track_id)  
                
               
                cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {car_id}", (int(x_min), int(y_min) - 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                
                if car_id in car_positions and 'position' in car_positions[car_id]:
                    prev_pos = car_positions[car_id]['position']
                    speed = calculate_speed(prev_pos, (center_x, center_y), frame_time, PIXELS_PER_METER)
                    label = f"Speed: {speed:.1f} km/h"
                    cv2.putText(frame, label, (int(x_min), int(y_min) - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                #
                car_positions[car_id] = {'position': (center_x, center_y), 'time': curr_time}
        
        
        car_positions = {k: v for k, v in car_positions.items() if curr_time - v['time'] < 1.0}
        prev_time = curr_time

        
        cv2.imshow('Car Speed Detection', frame)
        
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 0 for webcam else use path
    video_path = "/Users/akashsaha/Desktop/traffic_system/sample.mp4"
    process_video(video_path)