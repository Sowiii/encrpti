import face_recognition
import pickle
import cv2

# Open webcam and capture an image
video_capture = cv2.VideoCapture(0)
ret, frame = video_capture.read()
video_capture.release()

if not ret:
    print("❌ Error: Could not capture image from the webcam.")
    exit()

# Detect face and generate encoding
face_locations = face_recognition.face_locations(frame)
face_encodings = face_recognition.face_encodings(frame, face_locations)

if face_encodings:
    # Save the first detected face encoding
    with open("authorized_faces.pkl", "wb") as file:
        pickle.dump([face_encodings[0]], file)  # Save as a list

    print("✅ Face encoding saved successfully.")
else:
    print("❌ No face detected. Try again in better lighting.")
