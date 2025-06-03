import csv
import os
from datetime import datetime

def load_criminal_plates(criminal_file):
    """Load criminal license plates from CSV file"""
    criminal_plates = set()
    try:
        with open(criminal_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Skip empty rows
                    criminal_plates.add(row[0].strip().upper())
    except FileNotFoundError:
        print(f"Error: Criminal plates file '{criminal_file}' not found")
        return set()
    return criminal_plates

def check_detected_plates(detected_file, criminal_plates):
    """Check detected plates against criminal plates and return matches"""
    criminal_detections = []
    try:
        with open(detected_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Skip empty rows
                    timestamp, plate, confidence, vehicle_type, speed, violations = row
                    plate = plate.strip().upper()
                    if plate in criminal_plates:
                        criminal_detections.append({
                            'timestamp': timestamp,
                            'plate': plate,
                            'confidence': confidence,
                            'vehicle_type': vehicle_type,
                            'speed': speed,
                            'violations': violations
                        })
    except FileNotFoundError:
        print(f"Error: Detected plates file '{detected_file}' not found")
        return []
    return criminal_detections

def save_criminal_detections(criminal_detections, output_file):
    """Save criminal detections to CSV file"""
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'License Plate', 'Confidence', 'Vehicle Type', 'Speed', 'Violations'])
        for detection in criminal_detections:
            writer.writerow([
                detection['timestamp'],
                detection['plate'],
                detection['confidence'],
                detection['vehicle_type'],
                detection['speed'],
                detection['violations']
            ])

def main():
    # File paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    criminal_file = os.path.join(script_dir, 'criminal_plates.csv')
    detected_file = os.path.join(script_dir, 'detected_license_plates.csv')
    output_file = os.path.join(script_dir, 'criminal_detections.csv')
    
    # Load criminal plates
    criminal_plates = load_criminal_plates(criminal_file)
    if not criminal_plates:
        print("No criminal plates loaded. Exiting...")
        return
    
    # Check detected plates
    criminal_detections = check_detected_plates(detected_file, criminal_plates)
    
    # Save results
    save_criminal_detections(criminal_detections, output_file)
    
    # Print summary
    print(f"\nCriminal Detection Summary:")
    print(f"Total criminal plates in database: {len(criminal_plates)}")
    print(f"Total criminal detections found: {len(criminal_detections)}")
    print(f"\nDetected Criminal Vehicles:")
    for detection in criminal_detections:
        print(f"\nTimestamp: {detection['timestamp']}")
        print(f"License Plate: {detection['plate']}")
        print(f"Confidence: {detection['confidence']}")
        print(f"Vehicle Type: {detection['vehicle_type']}")
        print(f"Speed: {detection['speed']} km/h")
        print(f"Violations: {detection['violations']}")
        print("-" * 50)
    
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main() 