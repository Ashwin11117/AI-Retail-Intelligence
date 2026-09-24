import cv2
import sqlite3
from datetime import datetime
from ultralytics import solutions

def init_db():
    conn = sqlite3.connect('retailos.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Shopper_Logs (
            timestamp TEXT PRIMARY KEY,
            active_shoppers INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()
print("Initializing RetailOS Multi-Zone Intelligence Engine...")

cap = cv2.VideoCapture("D:/test.mp4")
if not cap.isOpened():
    print("CRITICAL ERROR: OpenCV cannot find or read the video file!")
    exit()

# Get video dimensions dynamically to cover the whole frame accurately
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Fallback if dimensions are 0
if frame_width == 0: frame_width = 1280
if frame_height == 0: frame_height = 720

# Define multi-zones scaled to video dimensions
multi_regions = {
    "Aisle_1": [(0, 0), (int(frame_width/2), 0), (int(frame_width/2), frame_height), (0, frame_height)],
    "Checkout": [(int(frame_width/2), 0), (frame_width, 0), (frame_width, frame_height), (int(frame_width/2), frame_height)]
}

region_counter = solutions.RegionCounter(
    show=True,
    region=multi_regions,
    model="yolov8n.pt",
    classes=[0]
)

print("Starting Multi-Zone Inference... Press 'q' to stop.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Video stream ended or failed to read frame.")
        break

    results = region_counter.process(frame)
    
    # Safely pull counts from region_counts dictionary
    total_active = 0
    if hasattr(region_counter, 'region_counts') and isinstance(region_counter.region_counts, dict):
        total_active = sum(region_counter.region_counts.values())

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('retailos.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO Shopper_Logs (timestamp, active_shoppers) VALUES (?, ?)", 
                   (timestamp, total_active))
    conn.commit()
    conn.close()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("RetailOS Engine Shutdown Safely.")
