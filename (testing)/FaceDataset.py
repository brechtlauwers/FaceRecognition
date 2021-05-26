import cv2
import os


webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

classifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')

cropSize = (128, 128)
pictureCount = 20

username = input('\n enter user name and press enter ==>  ')
username = username.replace(" ", "-").lower()
path = "../DeepLearning/dataset/" + username

if (os.path.exists(path)):
    print("\nThis name is already in our database...")
    exit(-1)
else:
    os.mkdir(path)

print("\nLook at the camera and wait ...")

count = 0


while(count < pictureCount):
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
        cv2.imwrite(path + '/' + str(count) + ".jpg", gray)
        cv2.imshow('image', frame)
        cv2.waitKey(1)


    cv2.waitKey(100)

print("\nReady!")
webcam.release()
cv2.destroyAllWindows()
