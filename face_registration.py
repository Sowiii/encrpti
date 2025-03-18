import face_recognition
import cv2
import pickle
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Load or create the authorized faces file
try:
    with open("authorized_faces.pkl", "rb") as file:
        authorized_faces = pickle.load(file)
except (FileNotFoundError, EOFError):  # If file doesn't exist or is empty
    authorized_faces = {}

# Get user input
name = input("Enter your name: ")

# Open the webcam
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("❌ Error: Could not access the camera!")
    exit(1)

print(f"📸 Look at the camera to register your face, {name}...")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("❌ Error: Camera read failed!")
        break

    # Detect face
    face_locations = face_recognition.face_locations(frame)
    if face_locations:
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        authorized_faces[name] = face_encoding  # Store encoding with name
        break

video_capture.release()
cv2.destroyAllWindows()

# Save updated dictionary to authorized_faces.pkl
with open("authorized_faces.pkl", "wb") as file:
    pickle.dump(authorized_faces, file)

print(f"✅ Face registered successfully for {name}!")
