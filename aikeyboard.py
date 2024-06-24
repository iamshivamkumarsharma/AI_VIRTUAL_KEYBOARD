import time

# Add a 2-second delay
time.sleep(2)

import cv2
import mediapipe as mp

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Function to draw a virtual keyboard in the middle of the screen with spacing between keys
def draw_keyboard(image, offset_x, offset_y):
    keys = [
        "1234567890",
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM",
        "#"  # Clear button
    ]
    key_width = 30
    key_height = 30
    key_spacing = 20  # Increased spacing between keys
    special_keys = {'#'}

    for row_idx, row in enumerate(keys):
        for col_idx, key in enumerate(row):
            x = offset_x + col_idx * (key_width + key_spacing)
            y = offset_y + row_idx * (key_height + key_spacing)
            color = (0, 0, 255) if key in special_keys else (255, 0, 0)
            cv2.rectangle(image, (x, y), (x + key_width, y + key_height), color, -1)  # Filled rectangle for key
            cv2.putText(image, key, (x + 5, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)  # Key label

    # Display message in the corner of the screen
    cv2.putText(image, "This is shivam AI keyboard,Press # for erase", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    return image


# Function to detect key presses
def detect_key_press(hand_landmarks, image, offset_x, offset_y, key_press_start_time, last_key, typed_text, delay=2):
    key_width = 30
    key_height = 30
    key_spacing = 20  # Increased spacing between keys
    keys = [
        "1234567890",
        "QWERTYUIOP",
        "ASDFGHJKL",
        "ZXCVBNM",
        "#"  # Clear button
    ]

    fingertip = hand_landmarks.landmark[8]  # Index finger tip
    px = int(fingertip.x * image.shape[1])
    py = int(fingertip.y * image.shape[0])

    for row_idx, row in enumerate(keys):
        for col_idx, key in enumerate(row):
            x = offset_x + col_idx * (key_width + key_spacing)
            y = offset_y + row_idx * (key_height + key_spacing)

            if x < px < x + key_width and y < py < y + key_height:
                cv2.rectangle(image, (x, y), (x + key_width, y + key_height), (0, 255, 0), -1)  # Highlight key
                cv2.putText(image, key, (x + 5, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

                if key == '#':  # Clear button pressed
                    typed_text = ""
                    return typed_text, time.time(), True  # Return True to indicate key press

                if len(key) == 1 and key.isalnum():  # Ensure only single alphanumeric characters are pressed
                    if last_key != key:
                        typed_text += key
                        return typed_text, time.time(), False  # Return False to continue typing

    return typed_text, key_press_start_time, False  # Return False by default


# Capture video from the webcam
cap = cv2.VideoCapture(0)
screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calculate offsets to center the keyboard
keyboard_width = 10 * (30 + 20) - 20  # 10 keys * (30 width + 20 spacing) - 20 spacing
keyboard_height = 5 * (30 + 20) - 20  # 5 rows * (30 height + 20 spacing) - 20 spacing
offset_x = (screen_width - keyboard_width) // 2
offset_y = (screen_height - keyboard_height) // 2

key_press_start_time = 0
last_key = None
typed_text = ""

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)

    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image and find hands
    results = hands.process(image_rgb)

    # Draw the virtual keyboard
    image = draw_keyboard(image, offset_x, offset_y)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            typed_text, key_press_start_time, key_pressed = detect_key_press(hand_landmarks, image, offset_x, offset_y,
                                                                              key_press_start_time, last_key,
                                                                              typed_text, delay=1)
            last_key = None  # Reset last_key after processing
            if key_pressed:
                break  # Exit the loop if a key is pressed

    # Display the typed text
    cv2.putText(image, typed_text, (50, screen_height - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Display the image
    cv2.imshow('Virtual Keyboard', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
