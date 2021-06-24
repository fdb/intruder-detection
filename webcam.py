import datetime

import cv2
import numpy as np
import requests

LAMP_ON_URL = 'https://maker.ifttt.com/trigger/lamp_on/with/key/bRWG-Z9VFdWKcG1_GlNpS9'
LAMP_OFF_URL = 'https://maker.ifttt.com/trigger/lamp_off/with/key/bRWG-Z9VFdWKcG1_GlNpS9'

last_event_time = datetime.datetime.now()
intruder_detected = False

def show_webcam(mirror=False):
    global last_event_time
    global intruder_detected
    cam = cv2.VideoCapture(0)
    prev_img = None
    while True:
        ret_val, img = cam.read()
        if mirror: 
            img = cv2.flip(img, 1)
        if prev_img is None:
            prev_img = img

        delta = cv2.subtract(prev_img, img)
        thresh = cv2.threshold(delta, 10, 255, cv2.THRESH_BINARY_INV)[1]
        count =  np.count_nonzero(thresh)
        changed_pixels = thresh.size - count

        now = datetime.datetime.now()
        time_delta = (now - last_event_time).seconds

        #print(thresh.size)
        #print(thresh.size - count)
        if changed_pixels > 100_000 and not intruder_detected and time_delta > 1:
            print("INTRUDER ALERT")
            requests.post(LAMP_OFF_URL)
            intruder_detected = True
            last_event_time = now
        elif changed_pixels < 100_000 and time_delta > 10:
            print("NOBODY THERE")
            requests.post(LAMP_ON_URL)
            intruder_detected = False
            last_event_time = now

        #print(thresh.size - count)
        #if thresh.size 
        
        cv2.imshow('my webcam', delta)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit

        prev_img = img


    cv2.destroyAllWindows()


def main():
    requests.post(LAMP_ON_URL)
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()