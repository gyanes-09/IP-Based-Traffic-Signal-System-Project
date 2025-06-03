from ultralytics import YOLO

# Load the trained model
model = YOLO("/Users/akashsaha/Desktop/traffic_system/runs/detect/train3/weights/best.pt")

# Perform inference (prediction)
results = model.predict(
    source="/Users/akashsaha/Desktop/traffic_system/Helmet_Detetction/3riders-2/test/images",  # Correct path formatting
    conf=0.25,  # Confidence threshold
    save=True    # Save results
)

# Display results
import glob
from IPython.display import Image, display

for image_path in glob.glob(f'{HOME}/runs/detect/predict/*.jpg')[:10]:
      display(Image(filename=image_path, width=600))
      print("\n")