import os
from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")
video_path = "input_videos/test_traffic.mp4"

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"❌ Could not open video: {video_path}")
    exit()

os.makedirs("output/annotated_videos", exist_ok=True)
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output/annotated_videos/test_traffic_out.mp4", fourcc, 20.0, (640, 480))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_resized = cv2.resize(frame, (640, 480))
    results = model(frame_resized)
    annotated_frame = results[0].plot()

    cv2.imshow("YOLOv8 Detection", annotated_frame)
    out.write(annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()