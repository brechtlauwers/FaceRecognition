from flask import Flask, render_template, request ,redirect, session, url_for, Response, flash
from flask_mysqldb import MySQL
import MySQLdb
import bcrypt
import cv2
import os
import glob
import time

classifier = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')

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
            session['email'] = email

            email = email.replace(" ", "-").lower()
            path = "../DeepLearning/dataset/" + email

            if (os.path.exists(path)):
                session.pop('_flashes', None)
                flash("This email is already in the database!")
                return render_template('register.html')
            else:
                os.mkdir(path)

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

@app.route('/register_webcam', methods=['GET', 'POST'])
def register_webcam():
    if request.method == "POST":
        email = session['email']
        images_path = os.path.join('.\dataset', email)
        if len(os.listdir(images_path)) == 6:
            session.pop('_flashes', None)
            flash("Your account has been made!")
            return redirect(url_for('index'))
        else:
            session.pop('_flashes', None)
            flash("Your face has not been recognized, retry!")
            return render_template("registerWebcam.html")

    return render_template("registerWebcam.html")

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        email = session['email']
        images_path = os.path.join('.\dataset', email)
        frame = []
        boxes = []

        f = glob.glob(os.path.join(images_path, "*"))
        for e in f:
            os.remove(e)

        img1 = request.files['img1']
        img2 = request.files['img2']
        img3 = request.files['img3']

        img1.save('%s/%s' % (images_path, ('%s-1.jpeg' % time.strftime("%Y%m%d-%H%M%S"))))
        img2.save('%s/%s' % (images_path, ('%s-2.jpeg' % time.strftime("%Y%m%d-%H%M%S"))))
        img3.save('%s/%s' % (images_path, ('%s-3.jpeg' % time.strftime("%Y%m%d-%H%M%S"))))

        imgarr = os.listdir(images_path)

        for current in range(len(imgarr)):
            buffer = os.path.join(images_path, imgarr[current])
            frame.append(cv2.imread(buffer))
            gray = cv2.cvtColor(frame[current], cv2.COLOR_BGR2GRAY)
            boxes.append(classifier.detectMultiScale(gray,
                                                     scaleFactor=1.1,
                                                     minNeighbors=5,
                                                     minSize=(60, 60),
                                                     flags=cv2.CASCADE_SCALE_IMAGE))
            print(boxes[current])
            if len(boxes[current]) == 1:
                for k in boxes[current]:
                    x, y, width, height = k
                    x2, y2 = x + width, y + height
                    cv2.rectangle(frame[current], (x, y), (x2, y2), (0, 0, 225), 1)
                    crop = cv2.resize(frame[current][y:y + height, x:x + width], (128, 128))

                cv2.imwrite("./dataset/" + email + "/facerecognition" + str(current) + ".jpg", crop)
            else:
                print('picture ' + str(current+1) + ' failed')
            cv2.waitKey(100)
    return render_template("login.html")

@app.route('/webcam_login', methods=['GET', 'POST'])
def webcamLogin():
    if request.method == 'POST':
        return render_template('profile.html')
    return render_template('loginWebcam.html')

@app.route('/verify', methods=['GET', 'POST'])
def webcamVerify():
    if request.method == 'POST':
        email = request.form['email']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM logininfo WHERE email=%s", [email])
        account = cursor.fetchone()

        if account is not None:
            if account['email'] == email:
                session['loginsuccess'] = True
                return redirect(url_for('profile'))
        else:
            session.pop('_flashes', None)
            flash("Your email has not been found.")
            return redirect(url_for('webcamLogin'))


    return render_template("loginWebcam.html")

if __name__ == '__main__':
    app.run(debug=True)
