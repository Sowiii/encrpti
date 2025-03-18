import cv2
import face_recognition
import pickle
import time
import sys
import numpy as np

# Ensure correct encoding for emoji support
sys.stdout.reconfigure(encoding="utf-8")

# Load authorized face encodings
try:
    with open("authorized_faces.pkl", "rb") as file:
        authorized_faces = pickle.load(file)

    # Ensure it's a dictionary with stored face encodings
    if not isinstance(authorized_faces, dict) or len(authorized_faces) == 0:
        raise ValueError("❌ Error: No registered faces found in authorized_faces.pkl!")

except (FileNotFoundError, ValueError) as e:
    print(f"❌ Error: {str(e)}")
    sys.stdout.flush()
    exit(1)

# Extract names and face encodings
known_names = list(authorized_faces.keys())
known_encodings = list(authorized_faces.values())

# Open webcam
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("❌ Error: Could not access the camera!")
    sys.stdout.flush()
    exit(1)

print("🔍 Scanning for face... (Will timeout in 5 seconds)")
sys.stdout.flush()

start_time = time.time()
face_detected = False
recognized_name = None

while time.time() - start_time < 5:  # 5-second timeout
    ret, frame = video_capture.read()

    if not ret:
        print("❌ Error: Camera read failed!")
        sys.stdout.flush()
        break

    # Detect faces
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if not face_encodings:  # Skip if no faces are found
        continue

    for face_encoding in face_encodings:
        # Compare faces using distance (lower is better)
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(distances)  # Get the best match

        if distances[best_match_index] < 0.35:  # Lower tolerance for better accuracy
            recognized_name = known_names[best_match_index]
            print(f"✅ Face recognized! Welcome, {recognized_name}! Access Granted.")
            sys.stdout.flush()
            face_detected = True
            break

    if face_detected:
        break  # Exit loop if a face is recognized

# Release the webcam properly before exiting
video_capture.release()
cv2.destroyAllWindows()

# If no face was detected after 5 seconds, deny access
if not face_detected:
    print("❌ No face detected! Access Denied.")
    sys.stdout.flush()
    exit(1)

exit(0)
