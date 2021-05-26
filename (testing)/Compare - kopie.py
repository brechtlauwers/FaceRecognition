import numpy as np
import cv2
import os
import dlib
import face_recognition

username = input('\n enter user name and press enter ==>  ')
username = username.replace(" ", "-").lower()
path = "../DeepLearning/dataset/" + username
path2 = "../DeepLearning/Fotos/"
counter = 1
access = 0

classifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cropSize = (128, 128)
pictureCount = 1

if (os.path.exists(path)):
    print("\nLook at the camera and wait, a picture will be taken in 5 seconds.")
    cv2.waitKey(5000)
    count = 0

    while (count < pictureCount):
        _, frame = webcam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=8)

        for i in boxes:
            print(i)
            x, y, width, height = i
            x2, y2 = x + width, y + height
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 1)
            count += 1

            gray = cv2.resize(gray[y:y + height, x:x + width], cropSize)
            cv2.imwrite(path2 + "testfoto.jpg", gray)
            cv2.imshow('image', frame)
            cv2.waitKey(1)

    print("\nReady!")
    webcam.release()
    cv2.destroyAllWindows()

    print("Comparing pictures...")

    testfoto = face_recognition.load_image_file("./Fotos/testfoto.jpg")
    testfoto_encoding = face_recognition.face_encodings(testfoto)[0]

    while(counter < 6):
        savedfoto = cv2.imread("./dataset/" + username + "/" + str(counter) + ".jpg")
        savedfoto_encoding = face_recognition.face_encodings(savedfoto)[0]
        results = face_recognition.compare_faces([savedfoto_encoding], testfoto_encoding)
        print(results)
        if (results[0] == True):
            access = access + 1
        counter = counter + 1
    
    if (access > 4):
        print("You are authenticated, welcome!")
    else:
        print("Sorry, your photo does not match with the owner of this profile.")
else:
    print("\nThis name does not have an account, make an account first!")
    exit(-1)
