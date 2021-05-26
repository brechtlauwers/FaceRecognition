import numpy as np
import cv2
import os
import dlib
import face_recognition

username = input('\nEnter user name and press enter ==>  ')
username = username.replace(" ", "-").lower()
path = "../DeepLearning/dataset/" + username
path2 = "../DeepLearning/Fotos/"
counter = 1
access = 0

classifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')
EyeCascade = cv2.CascadeClassifier('cascades/haarcascade_eye_tree_eyeglasses.xml')

cropSize = (128, 128)
pictureCount = 1

if (os.path.exists(path)):
    input("Press enter to take a picture.")
    webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
            cv2.imwrite(path2 + "testfoto1.jpg", gray)
            cv2.imshow('image', frame)
            cv2.waitKey(1)

    print("\nReady!")
    webcam.release()
    cv2.destroyAllWindows()

    print("Comparing pictures...")

    testfoto = face_recognition.load_image_file("./Fotos/testfoto1.jpg")
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
        print("We found a match, for extra safety reasons we will take another picture, pls close your eyes and open your mouth on this picure.")

        j = 1
        while (j == 1):
            input("Press enter to take a picture.")
            webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            _, frame = webcam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            boxes = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=8)

            for i in boxes:
                print(i)
                x, y, width, height = i
                x2, y2 = x + width, y + height
                cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 1)

                gray = cv2.resize(gray[y:y + height, x:x + width], cropSize)
                cv2.imwrite(path2 + "testfoto2.jpg", gray)
                cv2.imshow('image', frame)
                cv2.waitKey(1)

                print("\nReady!")
                webcam.release()
                cv2.destroyAllWindows()
            testfoto2 = cv2.imread("./Fotos/testfoto2.jpg")
            eyes = EyeCascade.detectMultiScale(
                frame,
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(30, 30),
            )
            if len(eyes) == 0:
                j = 2
                print("Congratulations, you are authenticated.")
            else:
                print("Failed, are you sure you had your eyes closed and mouth open? Please try again.")
    else:
        print("Sorry, your photo does not match with the owner of this profile. Please try again.")
else:
    print("\nThis name does not have an account, make an account first!")
    exit(-1)
