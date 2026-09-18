import cv2
import time

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start video capture (0 is usually the default USB camera)
print("Initializing camera...")
cap = cv2.VideoCapture(0)

time.sleep(2) # Give the camera a moment to warm up

print("Camera started! A window should pop up.")
print("Press 'q' in the video window to quit.")

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame. Is the camera connected or being used by another app?")
        break

    # Convert frame to grayscale (face detection works better in grayscale)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw a green rectangle around any detected faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, 'Face Detected', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the video feed with the drawn rectangles
    cv2.imshow('Arduino Hack - Face Recognition Test', frame)

    # Wait for the 'q' key to stop the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Quitting...")
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
