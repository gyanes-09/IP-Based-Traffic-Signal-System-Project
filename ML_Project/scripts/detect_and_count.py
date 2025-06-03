from ultralytics import YOLO
import cv2

def detect_and_count(video_path):
    model = YOLO('models/custom_model.pt')  # Load fine-tuned model
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        counts = {}
        for result in results:
            for obj in result.boxes.data:
                label = model.names[int(obj[5])]
                counts[label] = counts.get(label, 0) + 1

        print(f"Detected: {counts}")
        cv2.imshow('Detection', results.render()[0])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_and_count('data/test_videos/sample_video.mp4')
