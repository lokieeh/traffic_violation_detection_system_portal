import cv2
import os

video_path = "input_videos/test_traffic.mp4"

# Confirm file actually exists
if not os.path.exists(video_path):
    print(f"❌ File not found at: {video_path}")
    exit()

# Try to open video
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"❌ OpenCV cannot open video at: {video_path}")
else:
    print(f"✅ OpenCV successfully opened: {video_path}")

cap.release()