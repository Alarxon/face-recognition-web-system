#camera.py # import the necessary packages
import cv2 # defining face detector
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import pickle
import time
import cv2
import os
import mysql.connector

protoPath = "face_detection_model/deploy.prototxt"
modelPath = "face_detection_model/res10_300x300_ssd_iter_140000.caffemodel"
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath)

embedder = cv2.dnn.readNetFromTorch("openface_nn4.small2.v1.t7")

ds_factor=0.6

dic_tiempos = {}


class VideoCamera(object):
    def __init__(self):
       #capturing video
       self.video = VideoStream(src=0).start()
       time.sleep(2.0)
       self.fps = FPS().start()
       self.camara_nombre = ""

    def __del__(self):
        #releasing camera
        self.fps.stop()
        self.video.stop()

    def read_data(self):
        self.recognizer = pickle.loads(open("output/recognizer.pickle", "rb").read())
        self.le = pickle.loads(open("output/le.pickle", "rb").read())

    def set_nombre(self, nombre):
        self.camara_nombre = nombre

    def get_frame(self):
        
        #extracting frames
        frame = self.video.read()
        frame = imutils.resize(frame, width=600)

        (h, w) = frame.shape[:2]
        
        imageBlob = cv2.dnn.blobFromImage(
		    cv2.resize(frame, (300, 300)), 1.0, (300, 300),
		    (104.0, 177.0, 123.0), swapRB=False, crop=False)
        
        detector.setInput(imageBlob)
        detections = detector.forward()
        proba = 0
        name = ""

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
		    # filter out weak detections
            if confidence > 0.5: #CONFIDENCIA *****************************
			    # compute the (x, y)-coordinates of the bounding box for
			    # the face
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

			    # extract the face ROI
                face = frame[startY:endY, startX:endX]
                (fH, fW) = face.shape[:2]

			    # ensure the face width and height are sufficiently large
                if fW < 20 or fH < 20:
                    continue

			    # construct a blob for the face ROI, then pass the blob
			    # through our face embedding model to obtain the 128-d
			    # quantification of the face
                faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
                    (96, 96), (0, 0, 0), swapRB=True, crop=False)
                embedder.setInput(faceBlob)
                vec = embedder.forward()

			    # perform classification to recognize the face
                preds = self.recognizer.predict_proba(vec)[0]
                j = np.argmax(preds)
                proba = preds[j]
                name = self.le.classes_[j]

                global dic_tiempos
                if name in dic_tiempos:
                    if dic_tiempos[name] == 60:
                        dic_tiempos[name] = 0            

			    # draw the bounding box of the face along with the
			    # associated probability
                if proba >= 0.8:
                    if name not in dic_tiempos:
                        dic_tiempos[name] = 0
                    text = "Bienvenido " + name
                    y = startY - 10 if startY - 10 > 10 else startY + 10
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                        (0, 255, 0), 2)
                    cv2.putText(frame, text, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)
                    
                    if dic_tiempos[name] == 0:
                        print("SE GUARDO " + name)
                        mydb = mysql.connector.connect(
                            host="127.0.0.1",
                            user="sergio",
                            password="12345",
                            database="sistema"
                        )
                        mycursor = mydb.cursor()
                        sql = "INSERT INTO entradas (nombre,camara) VALUES (%s,%s)"
                        val = (str(name),str(self.camara_nombre))
                        mycursor.execute(sql, val)
                        mydb.commit()
                        dic_tiempos[name] = dic_tiempos[name] + 1
                else:
                    text = "{}: {:.2f}%".format(name, proba * 100)
                    y = startY - 10 if startY - 10 > 10 else startY + 10
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                        (0, 0, 255), 2)
                    cv2.putText(frame, text, (startX, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                
                if name in dic_tiempos:
                    if dic_tiempos[name] >= 1:
                        dic_tiempos[name] = dic_tiempos[name] + 1
        
        self.fps.update()

        # encode OpenCV raw frame to jpg and displaying it
        ret,jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


