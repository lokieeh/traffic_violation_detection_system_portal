import sys
import os
import cv2
import sqlite3
from datetime import datetime
from ultralytics import YOLO

def create_violations_table():
    conn = sqlite3.connect("violations.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            timestamp TEXT,
            image_path TEXT,
            video TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_violation(violation_type, timestamp, image_path, video_path):
    conn = sqlite3.connect("violations.db")
    c = conn.cursor()
    c.execute("INSERT INTO violations (type, timestamp, image_path, video) VALUES (?, ?, ?, ?)",
              (violation_type, timestamp, image_path, video_path))
    conn.commit()
    conn.close()

def detect_helmet(video_path):
    print("[INFO] Loading model...")
    model = YOLO("yolov8n.pt")  # Use your custom model if available

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Unable to open video file")

    os.makedirs("output/helmet_violations", exist_ok=True)

    # ✅ Create a dated snapshot folder
    date_folder = datetime.now().strftime("%Y-%m-%d")
    snapshot_folder = os.path.join("snapshots/helmet", date_folder)
    os.makedirs(snapshot_folder, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(3))
    height = int(cap.get(4))
    out_path = "output/helmet_output.mp4"
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    frame_num = 0
    snapshot_count = 0
    MAX_SNAPSHOTS = 5

    while cap.isOpened() and snapshot_count < MAX_SNAPSHOTS:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)[0]
        frame_with_boxes = results.plot()

        no_helmet_detected = False
        for box in results.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            if conf > 0.5:
                no_helmet_detected = True

        if no_helmet_detected and snapshot_count < MAX_SNAPSHOTS:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            snapshot_filename = f"helmet_violation_{frame_num}.jpg"
            snapshot_path = os.path.join(snapshot_folder, snapshot_filename)
            cv2.imwrite(snapshot_path, frame)
            log_violation("Helmet Violation", timestamp, snapshot_path, video_path)
            snapshot_count += 1

        out.write(frame_with_boxes)
        frame_num += 1

    cap.release()
    out.release()
    print(f"[INFO] Helmet detection completed. {snapshot_count} snapshots saved.")

if __name__ == "__main__":
    create_violations_table()

    if len(sys.argv) < 2:
        print("Usage: python helmet.py <video_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    try:
        detect_helmet(video_path)
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        sys.exit(1)