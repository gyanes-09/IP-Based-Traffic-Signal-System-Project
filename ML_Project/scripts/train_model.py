from ultralytics import YOLO

def train_model():
    model = YOLO('yolov10.pt')  # Load pre-trained YOLO model
    model.train(data='data/number_plate.yaml', epochs=50, imgsz=640)  # Fine-tune the model

if __name__ == "__main__":
    train_model()
