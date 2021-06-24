import cv2
import numpy as np
import paho.mqtt.client as mqtt

def on_connect(client, user_data, flags, rc):
    print("Connected to MQTT" + str(rc))
    client.publish("intruder", "connected")


client = mqtt.Client("webcam")
client.on_connect = on_connect
#client.on_message = on_message
# client.connect("mqtt.eclipseprojects.io", 1883, 60)
client.username_pw_set("lieme", "x7iNJWfycxrdEz51")
client.connect("lieme.cloud.shiftr.io", 1883, 60)

def show_webcam(mirror=False):
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

        #print(thresh.size)
        #print(thresh.size - count)
        if changed_pixels > 100_000:
            client.publish("intruder", changed_pixels)
            print("INTRUDER ALERT")

        #print(thresh.size - count)
        #if thresh.size 
        
        cv2.imshow('my webcam', delta)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit

        prev_img = img


    cv2.destroyAllWindows()


def main():
    client.loop_start()
    show_webcam(mirror=True)
    client.loop_stop()


if __name__ == '__main__':
    main()