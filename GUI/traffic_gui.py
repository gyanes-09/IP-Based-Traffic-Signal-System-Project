import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QWidget, QLabel, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time

class TrafficSystemThread(QThread):
    update_signal = pyqtSignal(str)
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self.process = None
        
    def run(self):
        # Get the path to the main script
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        main_script = os.path.join(script_dir, 'FINAL', 'test2.py')
        
        # Start the process with the video path
        self.process = subprocess.Popen(
            ['python', main_script, '--video_path', self.video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Read output line by line
        while self.running and self.process.poll() is None:
            line = self.process.stdout.readline()
            if line:
                self.update_signal.emit(line.strip())
                
    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()

class TrafficSystemGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Traffic Violation Detection System")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize variables
        self.video_path = ""
        self.process_thread = None
        self.vehicle_count = 0
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create top buttons layout
        buttons_layout = QHBoxLayout()
        
        # Video selection button
        self.select_video_btn = QPushButton("Select Video")
        self.select_video_btn.clicked.connect(self.select_video)
        buttons_layout.addWidget(self.select_video_btn)
        
        # Start button
        self.start_btn = QPushButton("Start Detection")
        self.start_btn.clicked.connect(self.start_detection)
        self.start_btn.setEnabled(False)
        buttons_layout.addWidget(self.start_btn)
        
        # Stop button
        self.stop_btn = QPushButton("Stop Detection")
        self.stop_btn.clicked.connect(self.stop_detection)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        
        layout.addLayout(buttons_layout)
        
        # Create status labels
        status_layout = QHBoxLayout()
        
        self.video_label = QLabel("No video selected")
        status_layout.addWidget(self.video_label)
        
        self.status_label = QLabel("Status: Ready")
        status_layout.addWidget(self.status_label)
        
        layout.addLayout(status_layout)
        
        # Create output display
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        layout.addWidget(self.output_display)
        
        # Create vehicle count display
        self.vehicle_count_label = QLabel("Vehicles Detected: 0")
        self.vehicle_count_label.setAlignment(Qt.AlignCenter)
        self.vehicle_count_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.vehicle_count_label)
        
    def select_video(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        
        if file_path:
            self.video_path = file_path
            self.video_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.start_btn.setEnabled(True)
            
    def start_detection(self):
        if not self.video_path:
            return
            
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_video_btn.setEnabled(False)
        self.status_label.setText("Status: Running")
        self.vehicle_count = 0
        self.vehicle_count_label.setText("Vehicles Detected: 0")
        
        # Start the detection process in a separate thread
        self.process_thread = TrafficSystemThread(self.video_path)
        self.process_thread.update_signal.connect(self.update_output)
        self.process_thread.start()
        
    def stop_detection(self):
        if self.process_thread:
            self.process_thread.stop()
            self.process_thread.wait()
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_video_btn.setEnabled(True)
        self.status_label.setText("Status: Stopped")
        
    def update_output(self, text):
        # Update the output display
        self.output_display.append(text)
        
        # Scroll to the bottom
        self.output_display.verticalScrollBar().setValue(
            self.output_display.verticalScrollBar().maximum()
        )
        
        # Check for vehicle count updates
        if "Vehicles:" in text:
            try:
                # Extract the number after "Vehicles:"
                count_text = text.split("Vehicles:")[1].strip()
                # Remove any non-numeric characters and convert to integer
                count = int(''.join(filter(str.isdigit, count_text)))
                self.vehicle_count = count
                self.vehicle_count_label.setText(f"Vehicles Detected: {count}")
                # Debug output
                self.output_display.append(f"DEBUG: Parsed count: {count} from text: {count_text}")
            except Exception as e:
                # Debug output for errors
                self.output_display.append(f"DEBUG: Error parsing count: {str(e)}")
                self.output_display.append(f"DEBUG: Original text: {text}")
                
    def closeEvent(self, event):
        # Stop the detection process if running
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.stop()
            # Wait for the thread to finish
            self.process_thread.wait()
            
        # Clean up any remaining resources
        if hasattr(self, 'process_thread'):
            del self.process_thread
            
        # Accept the close event
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TrafficSystemGUI()
    window.show()
    sys.exit(app.exec_())