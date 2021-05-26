import numpy as np
import cv2

classifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')      # cascade model wordt geladen

result = True
cropSize = (128, 128)

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)         # Webcam wordt geopend en foto wordt getrokken en opgeslagen

while(result):
    ret, frame = webcam.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    boxes = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6)     # gezicht wordt herkend
    cv2.putText(frame, "press 'q' to take a picture", (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))

    for i in boxes:
        print(i)
        x, y, width, height = i
        x2, y2 = x + width, y + height
        cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 1)  # vierkant rond gezicht tekenen

        cropped = gray[y:y + height, x:x + width]
        cropped = cv2.resize(cropped, cropSize)  # foto wordt geresized

        cv2.imwrite("webcam/" + str(width) + str(height) + "_faces.jpg", cropped)  # foto wordt opgeslagen

    cv2.imshow('frame', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):  # Als er op 'q' wordt gedrukt, dan neem je een foto + wordt opgeslagen
        cv2.imwrite('fotos/camera.jpg', cropped)
        result = False

webcam.release()
cv2.destroyAllWindows()
