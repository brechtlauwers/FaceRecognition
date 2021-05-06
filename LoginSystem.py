from flask import Flask, render_template, request ,redirect, session, url_for, Response
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt
import cv2
import os

def FaceDataset():
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
        ret, frame = webcam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6)

        for i in boxes:
            x, y, width, height = i
            x2, y2 = x + width, y + height
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 1)
            count += 1

            gray = cv2.resize(gray[y:y + height, x:x + width], cropSize)
            cv2.imwrite(path + '/' + str(count) + ".jpg", gray)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        cv2.waitKey(100)

    print("\nReady!")
    webcam.release()
    cv2.destroyAllWindows()



def FaceRecognition():
    classifier = cv2.CascadeClassifier('cascades/haarcascade_frontalface_default.xml')  # cascade model wordt geladen
    result = True
    cropSize = (128, 128)

    webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Webcam wordt geopend en foto wordt getrokken en opgeslagen

    while (result):
        ret, frame = webcam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        boxes = classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6)  # gezicht wordt herkend
        cv2.putText(frame, "press 'q' to take a picture", (200, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255))

        for i in boxes:
            print(i)
            x, y, width, height = i
            x2, y2 = x + width, y + height
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 1)  # vierkant rond gezicht tekenen

            cropped = gray[y:y + height, x:x + width]
            cropped = cv2.resize(cropped, cropSize)  # foto wordt geresized
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            cv2.imwrite("webcam/" + str(width) + str(height) + "_faces.jpg", cropped)  # foto wordt opgeslagen

        if cv2.waitKey(10) & 0xFF == ord('q'):  # Als er op 'q' wordt gedrukt, dan neem je een foto + wordt opgeslagen
            cv2.imwrite('fotos/camera.jpg', cropped)
            result = False

    webcam.release()
    cv2.destroyAllWindows()



app = Flask(__name__)
app.secret_key = "123435235"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "facerecognition01"
app.config["MYSQL_DB"] = "login"

db = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM logininfo WHERE email=%s", [username])
            account = cursor.fetchone()

            if account is not None:
                    if account['email'] == username and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
                        session['loginsuccess'] = True
                        return redirect(url_for('profile'))
            else:
                return redirect(url_for('index'))

    return render_template("login.html")

@app.route('/new', methods=['GET', 'POST'])
def new_user():
    if request.method == "POST":
        if "name" in request.form and "email" in request.form and "password" in request.form:
            username = request.form['name']
            email = request.form['email']
            password = request.form['password']
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cur.execute("INSERT INTO login.logininfo(name, password, email)VALUES(%s,%s,%s)",(username, hashed, email))
            db.connection.commit()
            return redirect(url_for('register_webcam'))
    return render_template("register.html")

@app.route('/new/profile')
def profile():
    if session['loginsuccess'] == True:
        return render_template("profile.html")

@app.route('/new/logout')
def logout():
    session.pop('loginsuccess', None)
    return redirect(url_for('index'))

@app.route('/register_webcam')
def register_webcam():
    return render_template("registerWebcam.html")

@app.route('/video_login')
def video_login():
    return render_template("loginWebcam.html")

@app.route('/live_video')
def live_video():
    return Response(FaceDataset(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/login_video')
def live_video2():
    return Response(FaceRecognition(), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(debug=True)