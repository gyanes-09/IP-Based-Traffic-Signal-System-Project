from ultralytics import YOLO
import cv2
import pytesseract
from database_utils import init_db, check_criminal_record

def process_video(video_path):
    model = YOLO('models/custom_model.pt')
    collection = init_db()
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        for result in results:
            for obj in result.boxes.data:
                x1, y1, x2, y2 = map(int, obj[:4])
                plate_crop = frame[y1:y2, x1:x2]
                text = pytesseract.image_to_string(plate_crop, config='--psm 7')
                record = check_criminal_record(collection, text.strip())
                print(f"Number Plate: {text.strip()}, Record: {record}")

        cv2.imshow('Pipeline', results.render()[0])
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_video('data/test_videos/sample_video.mp4')
