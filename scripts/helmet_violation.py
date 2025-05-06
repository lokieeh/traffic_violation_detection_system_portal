import os
from ultralytics import YOLO
import cv2

# 🧠 Load YOLOv8 model
model = YOLO("yolov8n.pt")  # You can switch to yolov8s/m/l for more accuracy

# 📂 Input video selection
video_folder = "input_videos"
video_files = [f for f in os.listdir(video_folder) if f.endswith(".mp4")]

if not video_files:
    print("❌ No video files found in input_videos/")
    exit()

print("\n📁 Available Videos:")
for idx, file in enumerate(video_files):
    print(f"{idx + 1}. {file}")

choice = input("\nEnter the number of the video you want to process: ")
try:
    selected_index = int(choice) - 1
    assert 0 <= selected_index < len(video_files)
except:
    print("❌ Invalid selection. Exiting.")
    exit()

selected_video = os.path.join(video_folder, video_files[selected_index])
print(f"\n▶️ Selected video: {selected_video}")

# 📹 Open video
cap = cv2.VideoCapture(selected_video)
if not cap.isOpened():
    print(f"❌ Could not open: {selected_video}")
    exit()

# 📁 Output folder
output_folder = "output/helmet_violations"
os.makedirs(output_folder, exist_ok=True)

violation_id = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    results = model(frame)
    detections = results[0].boxes.data

    motorcycles = []
    persons = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        cls = int(cls)
        if cls == 3:  # Motorcycle
            motorcycles.append((int(x1), int(y1), int(x2), int(y2)))
        elif cls == 0:  # Person
            persons.append((int(x1), int(y1), int(x2), int(y2)))

    for (mx1, my1, mx2, my2) in motorcycles:
        for (px1, py1, px2, py2) in persons:
            # Check if person is inside motorcycle bounding box
            if px1 > mx1 and px2 < mx2 and py2 < my2 + 40:
                violation_id += 1
                cv2.rectangle(frame, (mx1, my1), (mx2, my2), (0, 0, 255), 2)
                cv2.putText(frame, "No Helmet", (mx1, my1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Save violation image
                base_name = os.path.splitext(os.path.basename(selected_video))[0]
                save_path = os.path.join(output_folder, f"{base_name}_violation_{violation_id}.jpg")
                cv2.imwrite(save_path, frame)
                print(f"[!] Violation saved: {save_path}")
                break

    # 🔍 Live preview
    cv2.imshow("Helmet Violation Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()