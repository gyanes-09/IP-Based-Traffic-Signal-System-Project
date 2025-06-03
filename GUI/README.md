# Traffic Violation Detection System GUI

This is a graphical user interface for the Traffic Violation Detection System. It provides an easy way to run the detection system and monitor its output.

## Features

- Select video files through a file dialog
- Start and stop the detection system
- Real-time display of system output
- Vehicle count display
- Status monitoring

## Installation

1. Make sure you have Python 3.8 or higher installed
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the GUI application:
   ```bash
   python traffic_gui.py
   ```

2. Use the interface:
   - Click "Select Video" to choose a video file
   - Click "Start Detection" to begin processing
   - Click "Stop Detection" to stop the process
   - The output display shows real-time system messages
   - The vehicle count display shows the current number of detected vehicles

## Requirements

- PyQt5 for the GUI
- All dependencies from the main traffic system
- Video files in supported formats (mp4, avi, mov)

## Notes

- The GUI runs the main detection system in a separate process
- All output from the detection system is captured and displayed
- The vehicle count is updated in real-time
- The system can be stopped safely at any time 