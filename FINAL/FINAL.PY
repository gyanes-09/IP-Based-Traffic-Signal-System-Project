import torch
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
from time import time
from pymongo import MongoClient
import csv
import argparse
import os
from sort import Sort  # Assuming the SORT implementation is in a separate `sort.py` file
from datetime import datetime

# Device setup
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Constants
FPS = 30
PIXELS_PER_METER = 10
MIN_CONFIDENCE = 0.5
SPEED_LIMIT = 60  # km/h
LANE_BOUNDARY_Y = None  # Set dynamically for horizontal line
VEHICLES = [2, 3, 5, 7]  # COCO classes: car, motorcycle, bus, truck
PLATE_DETECTION_COOLDOWN = 2.0  # seconds to wait before detecting the same plate again

# Get the directory of the script for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# New constant for license plate CSV output
LICENSE_PLATE_CSV = os.path.join(SCRIPT_DIR, 'detected_license_plates.csv')

# Global dictionary to track recently detected plates
recent_plates = {}

# Load models
try:
    bike_detector = YOLO(os.path.join(SCRIPT_DIR, 'yolov8n.pt')).to(device)  # Generic object detection
    helmet_detector = YOLO(os.path.join(SCRIPT_DIR, 'helmet_detection.pt')).to(device)  # Pretrained helmet detection
    license_plate_detector = YOLO(os.path.join(SCRIPT_DIR, 'license_plate_detector.pt')).to(device)  # License plate detection
    person_detector = YOLO(os.path.join(SCRIPT_DIR, 'yolov8n.pt')).to(device)  # Person detection
    print("Models loaded successfully")
except Exception as e:
    print(f"Error loading models: {e}")
    raise

# Initialize OCR reader with fixed Pillow compatibility
try:
    # Patch for Pillow version compatibility
    import PIL
    if hasattr(PIL.Image, 'Resampling'):
        # For newer Pillow versions (9.0.0 and above)
        PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
        easyocr.utils.RESAMPLING_METHODS = {
            'NEAREST': PIL.Image.Resampling.NEAREST,
            'BILINEAR': PIL.Image.Resampling.BILINEAR,
            'BICUBIC': PIL.Image.Resampling.BICUBIC,
            'LANCZOS': PIL.Image.Resampling.LANCZOS,
            'ANTIALIAS': PIL.Image.Resampling.LANCZOS  # Map ANTIALIAS to LANCZOS
        }
    else:
        # For older Pillow versions
        easyocr.utils.RESAMPLING_METHODS = {
            'NEAREST': PIL.Image.NEAREST,
            'BILINEAR': PIL.Image.BILINEAR,
            'BICUBIC': PIL.Image.BICUBIC,
            'LANCZOS': PIL.Image.LANCZOS,
            'ANTIALIAS': PIL.Image.ANTIALIAS
        }
    
    reader = easyocr.Reader(['en'], gpu=True)
    print("OCR reader initialized")
except Exception as e:
    print(f"Error initializing OCR reader: {e}")
    raise

# MongoDB setup
def init_db():
    try:
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # Test the connection
        client.server_info()
        db = client['vehicle_data']
        return db['criminal_records']
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        print("Continuing without database functionality")
        return None

# Load criminal plates from CSV
def load_criminal_plates(file_path=None):
    if file_path is None:
        file_path = os.path.join(SCRIPT_DIR, 'criminal_plates.csv')
    
    criminal_plates = set()
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Check if row is not empty
                    criminal_plates.add(row[0].strip())
        print(f"Loaded {len(criminal_plates)} criminal plates")
    except Exception as e:
        print(f"Error loading criminal plates: {e}")
        print("Continuing with empty criminal plates set")
    
    return criminal_plates

# Modified: Initialize license plate CSV file with directory creation
def init_license_plate_csv(file_path=LICENSE_PLATE_CSV):
    try:
        # Create directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Check if file exists first
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                # Write header if creating a new file
                writer.writerow(['timestamp', 'license_plate', 'confidence', 'vehicle_type', 'speed', 'violations'])
                print(f"Created new license plate CSV file: {file_path}")
            else:
                print(f"Appending to existing license plate CSV file: {file_path}")
    except Exception as e:
        print(f"Error initializing license plate CSV: {e}")
        return None
    
    return file_path

# Modified: Save license plate to CSV with better error handling
def save_license_plate(file_path, plate_info):
    try:
        # Make sure all required fields exist
        required_fields = ['timestamp', 'plate_number', 'confidence', 'vehicle_type', 'speed', 'violations']
        for field in required_fields:
            if field not in plate_info:
                if field == 'violations':
                    plate_info[field] = []
                else:
                    plate_info[field] = "Unknown"
        
        # Convert violations list to string
        violations_str = ";".join(str(v) for v in plate_info['violations']) if plate_info['violations'] else "None"
        
        # Format speed with 1 decimal place
        speed_str = f"{float(plate_info['speed']):.1f}" if isinstance(plate_info['speed'], (int, float)) else plate_info['speed']
        
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                plate_info['timestamp'],
                plate_info['plate_number'],
                f"{float(plate_info['confidence']):.2f}" if isinstance(plate_info['confidence'], (int, float)) else plate_info['confidence'],
                plate_info['vehicle_type'],
                speed_str,
                violations_str
            ])
            print(f"License plate '{plate_info['plate_number']}' saved to CSV")
    except Exception as e:
        print(f"Error saving license plate to CSV: {e}")
        print(f"Attempted to save: {plate_info}")

# Helper functions
def calculate_speed(prev_position, curr_position, frame_time, pixels_per_meter):
    distance_pixels = np.sqrt((curr_position[0] - prev_position[0])**2 + 
                              (curr_position[1] - prev_position[1])**2)
    distance_meters = distance_pixels / pixels_per_meter
    speed_mps = distance_meters / frame_time
    return speed_mps * 3.6  # km/h

def check_violations(center_y, speed, frame_height):
    violations = []
    if speed > SPEED_LIMIT:
        violations.append(f"Speeding: {speed:.1f} km/h (> {SPEED_LIMIT} km/h)")
    if LANE_BOUNDARY_Y and (center_y < LANE_BOUNDARY_Y - 50 or center_y > LANE_BOUNDARY_Y + 50):
        violations.append("Lane Crossing")
    return violations

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

# Enhanced: Improved license plate detection with duplicate prevention
def detect_license_plate(frame):
    global recent_plates
    results = license_plate_detector(frame)
    detected_plates = []
    current_time = time()
    
    # Clean up old entries in recent_plates
    recent_plates = {plate: time for plate, time in recent_plates.items() 
                    if current_time - time < PLATE_DETECTION_COOLDOWN}
    
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            
            # Ensure coordinates are within frame boundaries
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
            
            # Check if the crop area is valid
            if x2 <= x1 or y2 <= y1 or x1 >= frame.shape[1] or y1 >= frame.shape[0]:
                continue
                
            license_plate_crop = frame[y1:y2, x1:x2]
            
            # Check if crop is not empty
            if license_plate_crop.size == 0:
                continue
            
            # Preprocess the license plate image to improve OCR
            # Convert to grayscale
            gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
                
            try:
                # Try OCR on both original and preprocessed images
                detections_original = reader.readtext(license_plate_crop)
                detections_processed = reader.readtext(denoised)
                
                # Combine and sort by confidence
                all_detections = detections_original + detections_processed
                all_detections.sort(key=lambda x: x[2], reverse=True)  # Sort by confidence
                
                for detection in all_detections:
                    bbox, text, score = detection
                    text = text.upper().replace(' ', '')
                    
                    # Filter out short or nonsensical plates
                    if len(text) >= 4 and any(c.isalnum() for c in text):
                        # Check if this plate was recently detected
                        if text in recent_plates:
                            last_detection_time = recent_plates[text]
                            if current_time - last_detection_time < PLATE_DETECTION_COOLDOWN:
                                continue  # Skip this plate if it was recently detected
                        
                        # Update the recent plates dictionary
                        recent_plates[text] = current_time
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        cv2.putText(frame, f"{text} ({score:.2f})", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                        
                        detected_plates.append({
                            'plate_number': text,
                            'confidence': score,
                            'bbox': (x1, y1, x2, y2)
                        })
                        break  # Use the highest confidence detection that passes filters
            except Exception as e:
                print(f"Error in OCR processing: {e}")
                # Continue with next detection even if this one fails
    
    return detected_plates, frame

def detect_triple_riding(frame):
    bike_results = bike_detector(frame)
    person_results = person_detector(frame)
    
    # Use list comprehensions to create proper lists, not iterators
    bikes = []
    for result in bike_results:
        for box in result.boxes:
            if int(box.cls[0]) == 3:  # Motorcycle class
                coords = box.xyxy[0].cpu().numpy()
                bikes.append((int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])))
    
    persons = []
    for result in person_results:
        for box in result.boxes:
            if int(box.cls[0]) == 0:  # Person class
                coords = box.xyxy[0].cpu().numpy()
                persons.append((int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])))
    
    violations = []
    for bx1, by1, bx2, by2 in bikes:
        person_count = 0
        for px1, py1, px2, py2 in persons:
            # Check if person bounding box overlaps significantly with bike
            # Using IoU (Intersection over Union) check
            x_overlap = max(0, min(bx2, px2) - max(bx1, px1))
            y_overlap = max(0, min(by2, py2) - max(by1, py1))
            
            if x_overlap > 0 and y_overlap > 0:
                overlap_area = x_overlap * y_overlap
                person_area = (px2 - px1) * (py2 - py1)
                
                # If at least 30% of the person is overlapping with the bike
                if overlap_area / person_area > 0.3:
                    person_count += 1
        
        if person_count > 2:
            violations.append((bx1, by1, bx2, by2))
    
    for bx1, by1, bx2, by2 in violations:
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 0, 255), 2)
        cv2.putText(frame, "Triple Riding Detected", (bx1, by1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    return frame, "Triple Riding" if violations else ""

def check_criminal_record(collection, plate_number):
    if collection is None:
        return "Database not available"
    try:
        record = collection.find_one({'plate_number': plate_number})
        return record if record else "No record found"
    except Exception as e:
        print(f"Error checking criminal record: {e}")
        return "Error checking records"

# MODIFIED: Process frame function to directly save detected license plates
def process_frame(frame, tracker, car_positions, collection, criminal_plates, frame_count, prev_time, csv_path):
    global LANE_BOUNDARY_Y
    # Initialize lane boundary as a horizontal line at the middle of the frame's height
    if frame_count == 1:
        LANE_BOUNDARY_Y = frame.shape[0] // 2  # Horizontal line position (middle of frame)

    curr_time = time()
    frame_time = curr_time - prev_time if frame_count > 1 else 1/FPS
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # Apply detections
    frame = detect_helmet(frame)
    detected_plates, frame = detect_license_plate(frame)  # Modified to return the frame as well
    frame, triple_riding = detect_triple_riding(frame)

    # IMPORTANT: Save any detected license plates immediately
    if detected_plates and csv_path:
        for plate_info in detected_plates:
            # Create a basic plate record with available information
            plate_data = {
                'timestamp': timestamp,
                'plate_number': plate_info['plate_number'],
                'confidence': plate_info['confidence'],
                'vehicle_type': "Unknown",  # Will be updated if we can associate with a vehicle
                'speed': 0,                # Will be updated if we can associate with a vehicle
                'violations': []           # Will be updated if we can associate with a vehicle
            }
            
            # Check if it's a criminal plate
            if plate_info['plate_number'] in criminal_plates:
                plate_data['violations'].append("Criminal Vehicle")
                print(f"Alert: Criminal vehicle detected - {plate_info['plate_number']}")
            
            # Save the plate info to CSV
            save_license_plate(csv_path, plate_data)

    # Vehicle detection and tracking
    try:
        detections = bike_detector(frame)[0]
        
        # Check if there are any detections
        if len(detections.boxes) > 0:
            detections_ = []
            vehicle_types = {}
            
            for box_data in detections.boxes.data.tolist():
                if len(box_data) >= 6 and int(box_data[5]) in VEHICLES:
                    x1, y1, x2, y2, score, class_id = box_data[:6]
                    class_id = int(class_id)
                    detections_.append([x1, y1, x2, y2, score])
                    
                    # Store vehicle type for each detection
                    vehicle_class_names = {2: "Car", 3: "Motorcycle", 5: "Bus", 7: "Truck"}
                    vehicle_types[(x1, y1, x2, y2)] = vehicle_class_names.get(class_id, "Vehicle")
            
            if detections_:
                track_ids = tracker.update(np.asarray(detections_))
                
                # Process tracked objects
                for track in track_ids:
                    x1, y1, x2, y2, track_id = map(int, track)
                    center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
                    
                    # Find the closest vehicle type match
                    vehicle_type = "Vehicle"
                    best_iou = 0
                    for box, vtype in vehicle_types.items():
                        # Calculate IoU
                        vx1, vy1, vx2, vy2 = box
                        x_overlap = max(0, min(x2, vx2) - max(x1, vx1))
                        y_overlap = max(0, min(y2, vy2) - max(y1, vy1))
                        
                        if x_overlap > 0 and y_overlap > 0:
                            overlap_area = x_overlap * y_overlap
                            box1_area = (x2 - x1) * (y2 - y1)
                            box2_area = (vx2 - vx1) * (vy2 - vy1)
                            iou = overlap_area / (box1_area + box2_area - overlap_area)
                            
                            if iou > best_iou:
                                best_iou = iou
                                vehicle_type = vtype
                    
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"ID: {track_id} ({vehicle_type})", (x1, y1 - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    # Speed calculation - use moving average for stability
                    speed = 0
                    violations = []
                    
                    if track_id in car_positions:
                        prev_pos = car_positions[track_id]['position']
                        prev_speed = car_positions[track_id].get('speed', 0)
                        
                        # Calculate current speed
                        current_speed = calculate_speed(prev_pos, (center_x, center_y), frame_time, PIXELS_PER_METER)
                        
                        # Apply moving average for stability (80% previous, 20% current)
                        if prev_speed > 0:
                            speed = 0.8 * prev_speed + 0.2 * current_speed
                        else:
                            speed = current_speed
                            
                        # Constrain speed to reasonable values to eliminate spikes
                        if abs(speed - prev_speed) > 10 and prev_speed > 0:
                            speed = prev_speed
                        
                        cv2.putText(frame, f"Speed: {speed:.1f} km/h", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        # Check for violations
                        violations = check_violations(center_y, speed, frame.shape[0])
                        if triple_riding:
                            violations.append(triple_riding)
                            
                        for i, violation in enumerate(violations):
                            cv2.putText(frame, violation, (x1, y1 - 40 - i*15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        
                    # Update vehicle information
                    car_positions[track_id] = {
                        'position': (center_x, center_y), 
                        'time': curr_time,
                        'speed': speed,
                        'vehicle_type': vehicle_type,
                        'violations': violations,
                        'bbox': (x1, y1, x2, y2)
                    }
                        
                    # Association of license plates with vehicles (for updating the CSV later)
                    for plate_info in detected_plates:
                        px1, py1, px2, py2 = plate_info['bbox']
                        # Check if the license plate is inside or overlapping with this vehicle
                        if (px1 >= x1 and px2 <= x2 and py1 >= y1 and py2 <= y2) or \
                           (max(0, min(px2, x2) - max(px1, x1)) > 0 and max(0, min(py2, y2) - max(py1, y1)) > 0):
                            
                            # Add the vehicle info to the already saved plate
                            updated_plate_data = {
                                'timestamp': timestamp,
                                'plate_number': plate_info['plate_number'],
                                'confidence': plate_info['confidence'],
                                'vehicle_type': vehicle_type,
                                'speed': speed,
                                'violations': violations
                            }
                            
                            # Include criminal vehicle status if needed
                            if plate_info['plate_number'] in criminal_plates:
                                cv2.putText(frame, "CRIMINAL VEHICLE", (x1, y1 - 55), 
                                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                if "Criminal Vehicle" not in violations:
                                    updated_plate_data['violations'].append("Criminal Vehicle")
                            
                            # Save updated information in a new row (this creates a history of the plate with updated info)
                            save_license_plate(csv_path, updated_plate_data)
            else:
                # No vehicles detected
                track_ids = tracker.update(np.empty((0, 5)))
        else:
            # No detections at all
            track_ids = tracker.update(np.empty((0, 5)))
    except Exception as e:
        print(f"Error in vehicle detection and tracking: {e}")
        track_ids = []

    # Clean up old positions
    car_positions = {k: v for k, v in car_positions.items() if curr_time - v['time'] < 1.0}
    
    # Draw the horizontal lane boundary line
    cv2.line(frame, (0, LANE_BOUNDARY_Y), (frame.shape[1], LANE_BOUNDARY_Y), (255, 0, 0), 2)
    
    return frame, curr_time

def main():
    parser = argparse.ArgumentParser(description="Traffic Violation Detection System")
    parser.add_argument('--video', type=str, default='sample.mp4', help='Path to video file or 0 for webcam')
    parser.add_argument('--criminal_plates', type=str, default=None, help='Path to criminal plates CSV')
    parser.add_argument('--output_csv', type=str, default=LICENSE_PLATE_CSV, help='Path to output CSV for detected license plates')
    args = parser.parse_args()

    # Initialize components
    try:
        tracker = Sort(max_age=1, min_hits=3, iou_threshold=0.3)
    except Exception as e:
        print(f"Error initializing SORT tracker: {e}")
        print("Make sure sort.py is in the same directory")
        return

    collection = init_db()
    criminal_plates = load_criminal_plates(args.criminal_plates)
    csv_path = init_license_plate_csv(args.output_csv)
    
    # Handle video input
    video_path = args.video
    if video_path == '0':
        video_path = 0
    elif not os.path.isabs(video_path):
        video_path = os.path.join(SCRIPT_DIR, video_path)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video source {video_path}.")
        return

    # Set video properties for better performance
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    car_positions = {}
    frame_count = 0
    prev_time = time()
    
    # Initialize the lane boundary to None, will be set when first frame is processed
    global LANE_BOUNDARY_Y
    LANE_BOUNDARY_Y = None

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("End of video stream")
                break
            
            frame_count += 1
            
            # Initialize lane boundary on first frame
            if frame_count == 1:
                LANE_BOUNDARY_Y = frame.shape[0] // 2

            try:
                frame, prev_time = process_frame(frame, tracker, car_positions, collection, criminal_plates, frame_count, prev_time, csv_path)
            except Exception as e:
                print(f"Error processing frame {frame_count}: {e}")
                continue

            cv2.imshow("Traffic Violation Detection", frame)

            # Check for quit with a small delay
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("User requested exit")
                break

    except KeyboardInterrupt:
        print("Processing interrupted by user")
    except Exception as e:
        print(f"Unexpected error during video processing: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"Processing complete. License plates saved to {csv_path}")

if __name__ == "__main__":
    main()