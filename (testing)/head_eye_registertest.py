from flask import Flask, render_template, request ,redirect, session, url_for, Response, flash
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt
import cv2
import os
import glob
import time
import dlib
import face_recognition

classifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
EyeCascade = cv2.CascadeClassifier('cascades/haarcascade_eye_tree_eyeglasses.xml')

images_path = cv2.imread('./dataset/test14@gmail.com/eyes_picture.jpg')
gray = cv2.cvtColor(images_path, cv2.COLOR_BGR2GRAY)

cropSize = (128, 128)
count = 0

boxes = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4)
for i in boxes:
            print(i)
            x, y, width, height = i
            x2, y2 = x + width, y + height
            cv2.rectangle(images_path, (x, y), (x2, y2), (0, 0, 225), 1)
            count += 1

            gray = cv2.resize(gray[y:y + height, x:x + width], cropSize)
            
            cv2.waitKey(1)
print(boxes)

if len(boxes) == True:
    eyes = EyeCascade.detectMultiScale(
    images_path,
    scaleFactor=1.1,
    minNeighbors=3,
    minSize=(30, 30),
    )
    if len(eyes) == 0:     
        print("Congratulations, you are authenticated.")
    else:
        print("Failed, are you sure you had your eyes closed and mouth open? Please try again.")
else:
    print(" no head found")


