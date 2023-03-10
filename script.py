import cv2
import imutils
import threading
import winsound

# Set up camera
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Set window widht / height
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 50000)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 4000)

# Starting Frame
# Get frame and compare it to next frame in order to calculate the difference and 'detect motion'
# if the differences exceed the threshold (motion detected) set the alarm

_, baseline_frame = capture.read()
# Resize every frame to 500 for comparaison to standardized format
baseline_frame = imutils.resize(baseline_frame, width=500)
 
# Convert to grayscale to and blur to smooth the image
# Because we are interested in motion we do not need RGB colors
baseline_frame = cv2.cvtColor(baseline_frame, cv2.COLOR_BGR2GRAY)
baseline_frame = cv2.GaussianBlur(baseline_frame, (21, 21), 0)

# Flags to check if the events are hapenning
is_ringing = False
is_active = False
# Counts the number of frames that motion has been detected
motion_counter = 0

# What happens when alarm happens
# Even if it captures small movement it will beep 5 times
# For constant movement -> constant function calls -> constant beeps
def ring():
    global is_ringing
    for _ in range(5):
        if is_active:
            winsound.Beep(2500, 1000)
        else:
            break
    is_ringing = False

# In order to achieve a continuous data stream
while True:
    # Capture frame and resize
    _, current_frame = capture.read()
    current_frame = imutils.resize(current_frame, width=500)
    # In order to create a single frame delay
    counter = 0
    if is_active:
        counter += 1
        # Grayscale and blur the frame
        gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
        # Calculate diff
        difference = cv2.absdiff(gray_frame, baseline_frame)
        # To have either 255 or 0 we instanciate a black and white threshold
        # > threshold -> 255
        # < threshold -> 0
        threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        print(threshold.sum())
        baseline_frame = gray_frame

        # The smaller the number the more sensitive to motion
        if threshold.sum() > 300:
            motion_counter += 1
        else:
            # If we dont have consistent movement decrement counter
            if motion_counter > 0 and counter % 2 == 0:
                motion_counter -= 1 

        cv2.imshow('CCTV', threshold)
    else:
        cv2.imshow('CCTV', current_frame)

    # if we have consistent motion for 20 frames or more set the alarm
    if motion_counter > 20:
        if not is_ringing:
            is_ringing = True
            threading.Thread(target=ring).start()
    
    user_input = cv2.waitKey(30)
    # Y to start the program and Q to quit 
    if user_input == ord('y'):
        is_active = not is_active
        motion_counter = 0
    if user_input == ord('q'):
        is_active = False
        break

capture.release()
cv2.destroyAllWindows()