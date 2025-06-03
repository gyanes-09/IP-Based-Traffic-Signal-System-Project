from flask import Flask, jsonify
import threading
import main  # Import main.py as a module

app = Flask(__name__)

# Global variable to store detection results
detection_results = {}

def run_detection():
    """Function to run vehicle detection and store results globally."""
    global detection_results
    detection_results = main.detect_vehicles()

# Run `main.py` in a separate thread when the Flask app starts
threading.Thread(target=run_detection, daemon=True).start()

@app.route('/detect', methods=['GET'])
def detect():
    """Endpoint to get the detection results in JSON format."""
    return jsonify(detection_results)

if __name__ == '__main__':
    app.run(debug=True)
