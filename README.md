# Traffic Violation Detection System

An intelligent traffic monitoring system that detects multiple types of traffic violations, tracks vehicles, and manages traffic signals based on traffic density.

## Features

- **Vehicle Detection and Tracking**
  - Real-time detection of cars, motorcycles, buses, and trucks
  - Vehicle tracking with unique IDs
  - Speed calculation for each vehicle

- **Violation Detection**
  - Speeding violations
  - Lane crossing detection
  - Helmet usage monitoring for motorcycles
  - Triple riding detection on motorcycles
  - License plate recognition and tracking

- **Smart Traffic Signal System**
  - Adaptive traffic signal timing based on vehicle density
  - Different weightage for various vehicle types:
    - Cars: 1.0
    - Motorcycles: 0.5
    - Buses: 2.0
    - Trucks: 1.5
  - Real-time vehicle counting when crossing detection line
  - Visual traffic signal display with timing information

- **Criminal Vehicle Detection**
  - License plate matching against database of criminal vehicles
  - Real-time alerts for detected criminal vehicles
  - MongoDB integration for criminal records

## Prerequisites

```bash
# Required Python packages
pip install torch torchvision
pip install ultralytics
pip install easyocr
pip install opencv-python
pip install pymongo
pip install numpy
pip install sort-tracker
```

## Required Model Files

Place these model files in the same directory as the script:
- `yolov8n.pt` - General object detection
- `helmet_detection.pt` - Helmet detection
- `license_plate_detector.pt` - License plate detection

## Configuration

Key parameters that can be adjusted in the code:
```python
# Speed and timing constants
FPS = 30
SPEED_LIMIT = 60  # km/h
MIN_GREEN_TIME = 20  # seconds
MAX_GREEN_TIME = 60  # seconds
YELLOW_TIME = 3  # seconds
RED_TIME = 5  # seconds

# Vehicle detection settings
MIN_CONFIDENCE = 0.5
VEHICLE_THRESHOLD = 5  # Minimum vehicles for traffic density calculation
```

## Usage

```bash
python final1.py [options]

Options:
  --video PATH           Path to video file or 0 for webcam (default: 'sample.mp4')
  --criminal_plates PATH Path to CSV file containing criminal license plates
  --output_csv PATH     Path for saving detected license plates
```

## Output

1. **Visual Display**
   - Bounding boxes around detected vehicles
   - Vehicle IDs and types
   - Speed measurements
   - Violation warnings
   - Traffic signal status
   - Vehicle counts and weighted traffic density

2. **CSV Output**
   - Timestamp
   - License plate number
   - Confidence score
   - Vehicle type
   - Speed
   - Detected violations

## Database Integration

The system uses MongoDB to store and check criminal vehicle records:
- Database: 'vehicle_data'
- Collection: 'criminal_records'
- Connection: localhost:27017

## File Structure

```
traffic_system/
├── FINAL/
│   ├── final1.py          # Main script
│   ├── sort.py            # SORT tracking implementation
│   └── criminal_plates.csv # List of criminal plates
├── model/
│   ├── yolov8n.pt
│   ├── helmet_detection.pt
│   └── license_plate_detector.pt
└── README.md
```

## Violation Detection Logic

1. **Speed Violation**
   - Calculated using pixel-to-meter conversion
   - Triggers when speed > SPEED_LIMIT

2. **Lane Crossing**
   - Detected when vehicle crosses boundary line
   - Uses center point of vehicle bounding box

3. **Helmet Detection**
   - Applied to detected motorcycles
   - Uses dedicated helmet detection model

4. **Triple Riding**
   - Counts persons on motorcycles
   - Triggers when count > 2

## Traffic Signal Algorithm

1. Signal changes based on:
   - Vehicle count
   - Weighted vehicle density
   - Minimum and maximum timing constraints

2. Timing calculation:
   ```python
   if weighted_count > VEHICLE_THRESHOLD:
       green_time = min(MAX_GREEN_TIME, MIN_GREEN_TIME + (weighted_count - VEHICLE_THRESHOLD) * 2)
   else:
       green_time = MIN_GREEN_TIME
   ```

## Known Limitations

- Requires good lighting conditions for optimal detection
- License plate recognition accuracy depends on image quality
- Vehicle speed calculation assumes fixed camera position
- Requires calibration for different camera angles

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 