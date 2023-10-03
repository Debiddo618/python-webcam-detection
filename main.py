import glob
import os
import time
import cv2
from emailing import send_email
import os
from threading import Thread

video = cv2.VideoCapture(0)
time.sleep(1)
first_frame = None
count = 1
status_list = []


def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)


while True:
    status = 0
    # capturing the first frame
    check, frame = video.read()

    # make a gray frame
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # blur the gray frame
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # if setting the first frame
    if first_frame is None:
        first_frame = gray_frame_gau

    # show the difference between first frame and the current frame
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    # cv2.imshow("My video", delta_frame)

    # change all pixel with 40 or more to 255
    thresh_frame = cv2.threshold(delta_frame, 40, 255, cv2.THRESH_BINARY)[1]

    # dilating the image
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    # finding the contours
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        # do nothing if area of contour is less than 5000
        if cv2.contourArea(contour) < 5000:
            continue
        # making a green box around contours
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0))

        if rectangle.any():
            status = 1
            # storing image
            cv2.imwrite(f"images/{count}.png", frame)
            count += 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0:
        email_thread = Thread(target=send_email, args=(image_with_object,))
        email_thread.daemon = True
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True
        email_thread.start()

    # show the original frame with green box
    cv2.imshow("My video", frame)

    # press "q" to quit the program
    key = cv2.waitKey(1)
    if key == ord("q"):
        break
video.release()
try:
    email_thread.join()
    clean_thread.start()
    clean_thread.join()
except:
    print("No image")

# cv2.imwrite("image.png",frame)
