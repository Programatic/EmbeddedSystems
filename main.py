from threading import Thread
import cv2
import numpy as np
import collections
import datetime
import base64
import smtplib, ssl
from enum import Enum
import server

PASSWORD = 'CSDSSECUREWAREHOUSE'

port = 465
context = ssl.create_default_context()

smserver = smtplib.SMTP_SSL("smtp.gmail.com", port, context=context)
smserver.login("securewarehousecsds@gmail.com", PASSWORD)

CAM1 = 1

def sendAlert():
    try:
        smserver.sendmail("securewarehousecsds@gmail.com", server.alert_to, 
        """
        Subject: Urgent! Thread Identified

        There is a threat aproaching the warehouse!
        """
        )
    except:
        pass

class EventState(Enum):
    LOW = 0,
    MEDIUM = 1,
    HIGH = 2

faceCascade = cv2.CascadeClassifier("haarcascade_upperbody.xml")

event_state = EventState.LOW

def start(cam):
    global event_state

    intruder = ()
    last_seen = datetime.datetime.now()

    deque = collections.deque(maxlen=10)

    video_capture = cv2.VideoCapture(cam)

    frame_width = int(video_capture.get(3))
    frame_height = int(video_capture.get(4))
   
    size = (frame_width, frame_height)

    outVid = None

    while True:
        _, frames = video_capture.read()
        image_small = cv2.resize(frames, (256, 192), interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(image_small, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0 and datetime.datetime.now() - datetime.timedelta(seconds = 1) > last_seen:
            intruder = ()
            event_state = EventState.LOW

            if outVid is not None:
                outVid.release()        
                outVid = None

        for (x, y, w, h) in faces:
            (x,y,w,h) = [int(round(i * 2.5)) for i in (x, y, w, h)]
            deque.append(w)

            cv2.rectangle(frames, (x, y), (x+w, y+h), (0, 255, 0), 2)
            if not intruder:
                intruder = (x, y, w, h)
                event_state = EventState.MEDIUM
            elif x - intruder[0] < 30 and y - intruder[1] < 30:
                last_seen = datetime.datetime.now()
                average = np.average(deque)
                if w - average > 10:
                    event_state = EventState.HIGH
                    print("Intruder is approaching", w - intruder[2], h - intruder[3])
                    Thread(target = sendAlert).start()

                intruder = (x, y, w, h)

        if event_state == EventState.MEDIUM or event_state == EventState.HIGH:
            if outVid is None:
                outVid = cv2.VideoWriter(f'./vids/{ datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") }.mp4', 
                         cv2.VideoWriter_fourcc(*'mp4v'),
                         30, size)

            outVid.write(frames) 

        _, buffer = cv2.imencode('.jpg', frames)
        server.frame = base64.b64encode(buffer).decode("utf-8")

        cv2.imshow('Video', frames)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    if outVid is not None:
        outVid.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    t1 = Thread(target = start, args=[2])
    # t2 = Thread(target = start, args=[]) 
    server.run_web_server()

    t1.start()
    # t2.start()
    t1.join()
    # t2.join()