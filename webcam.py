import datetime
from os import system
import subprocess

import cv2
import numpy as np
import requests

LAMP_ON_URL = 'https://maker.ifttt.com/trigger/lamp_on/with/key/bRWG-Z9VFdWKcG1_GlNpS9'
LAMP_OFF_URL = 'https://maker.ifttt.com/trigger/lamp_off/with/key/bRWG-Z9VFdWKcG1_GlNpS9'

last_event_time = datetime.datetime.now()

STATE_NOBODY_HERE = "nobody_here"
STATE_INTRUDER_DETECTED = "intruder_detected"

state = STATE_NOBODY_HERE


PIXEL_CHANGE_THRESHOLD = 50_000


def turn_led_on():
    system('/opt/vc/bin/vcmailbox 0x00038041 8 8 130 1')


def turn_led_off():
    system('/opt/vc/bin/vcmailbox 0x00038041 8 8 130 0')


def show_webcam(mirror=False):
    global state
    cam = cv2.VideoCapture(0)
    prev_img = None
    skip_frames = 0
    while True:
        ret_val, img = cam.read()
        if skip_frames > 0:
            prev_img = img
            skip_frames -= 1
            continue
        if mirror:
            img = cv2.flip(img, 1)
        if prev_img is None:
            prev_img = img

        delta = cv2.subtract(prev_img, img)
        thresh = cv2.threshold(delta, 10, 255, cv2.THRESH_BINARY_INV)[1]
        count = np.count_nonzero(thresh)
        changed_pixels = thresh.size - count
        print(changed_pixels)

        now = datetime.datetime.now()

        if state == STATE_NOBODY_HERE:
            if changed_pixels > PIXEL_CHANGE_THRESHOLD:
                state = STATE_INTRUDER_DETECTED
                print("INTRUDER ALERT")
                turn_led_off()
                requests.post(LAMP_OFF_URL)
                timer_start = now

        elif state == STATE_INTRUDER_DETECTED:
            time_delta = (now - timer_start).seconds
            if time_delta > 10:
                if changed_pixels > PIXEL_CHANGE_THRESHOLD:
                    print("...INTRUDER IS STILL HERE...")
                    timer_start = now
                else:
                    print("NOBODY HERE")
                    turn_led_on()
                    requests.post(LAMP_ON_URL)
                    skip_frames = 100
                    prev_img = img
                    state = STATE_NOBODY_HERE

        cv2.imshow('my webcam', delta)
        if cv2.waitKey(1) == 27:
            break  # esc to quit

        prev_img = img

    cv2.destroyAllWindows()


def main():
    turn_led_on()
    requests.post(LAMP_ON_URL)
    show_webcam(mirror=True)


if __name__ == '__main__':
    main()
