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

# cascade model van gezicht en ogen wordt geladen
classifier = cv2.CascadeClassifier('Cascades/haarcascade_frontalface_default.xml')
EyeCascade = cv2.CascadeClassifier('cascades/haarcascade_eye_tree_eyeglasses.xml')

# verbinding maken en inloggen met MYSQL database via Flask
app = Flask(__name__)
app.secret_key = "123435235"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "facerecognition01"
app.config["MYSQL_DB"] = "login"

db = MySQL(app)



# --HOMEPAGE--
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Javascript stuurt POST request met username (email) en wachtwoord van gebruiker
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']

            # gegeven email wordt in database gezocht
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM logininfo WHERE email=%s", [username])
            account = cursor.fetchone()

            # nakijken ofdat account met dit email adres bestaat
            if account is not None:
                    if account['email'] == username and bcrypt.checkpw(password.encode('utf-8'), account['password'].encode('utf-8')):
                        # gehashte wachtwoord wordt vergeleken en toegang tot account als dit overeenkomstig is
                        session['loginsuccess'] = True
                        return redirect(url_for('profile'))
            else:
                # refresh als account niet bestaat
                return redirect(url_for('index'))

    return render_template("login.html")


# --REGISTER PAGE--
@app.route('/new', methods=['GET', 'POST'])
def new_user():
    if request.method == "POST":
        # Javascript stuurt POST request met username, email en wachtwoord van gebruiker
        if "name" in request.form and "email" in request.form and "password" in request.form:
            username = request.form['name']
            email = request.form['email']
            password = request.form['password']
            # email wordt in 'session variable' opgeslagen zodat dit verder nog gebruikt kan worden
            session['email'] = email

            # spaties en hoofdletters worden uit email gehaald als dit het geval is
            email = email.replace(" ", "-").lower()
            path = "../DeepLearning/dataset/" + email

            # persoonlijke directory wordt aangemaakt voor het account als dit nog niet bestaat
            if (os.path.exists(path)):
                session.pop('_flashes', None)
                flash("This email is already in the database!")
                # als gebruiker al bestaat, error message wordt getoond
                return render_template('register.html')
            else:
                os.mkdir(path)

            # database raadplegen
            cur = db.connection.cursor(MySQLdb.cursors.DictCursor)
            # wachtwoord hashen voor veiligheid
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # gebruiker toevoegen aan database
            cur.execute("INSERT INTO login.logininfo(name, password, email)VALUES(%s,%s,%s)",(username, hashed, email))
            db.connection.commit()
            # doorverwijzen naar register webcam
            return redirect(url_for('register_webcam'))
    return render_template("register.html")


# --ACCOUNT PAGE--
@app.route('/new/profile')
def profile():
    if session['loginsuccess'] == True:
        return render_template("profile.html")


# --LOGOUT--
@app.route('/new/logout')
def logout():
    # uitloggen zorgt ervoor dat je niet meer terug naar je account kan zonder terug in te loggen
    session.pop('loginsuccess', None)
    session.pop('access', None)
    # doorverwijzen naar homepage
    return redirect(url_for('index'))


# --REGISTER WITH WEBCAM--
@app.route('/register_webcam', methods=['GET', 'POST'])
def register_webcam():
    if request.method == "POST":
        # email wordt via session variable terug opgevraagd
        email = session['email']
        images_path = os.path.join('.\dataset', email)

        #we checken of op de laatste foto die getrokken is bij het regristreren de ogen gesloten zijn
        image_eye = cv2.imread(images_path + "/eyes_picture.jpg")
        eyes = EyeCascade.detectMultiScale(
            image_eye,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(30, 30),
        )

        #indien de ogen gesloten zijn gaat het programma verder met regristratie
        if len(eyes) == 0:
            # nakijken ofdat er 11 foto's in de directory zitten
            # als dit niet het geval is wil het zeggen dat er een gezicht niet herkend werd
            if len(os.listdir(images_path)) == 11:
                session.pop('_flashes', None)
                flash("Your account has been made!")
                os.remove(images_path + '/facerecognition0.jpg')
                os.remove(images_path + '/facerecognition1.jpg')
                os.remove(images_path + '/facerecognition2.jpg')
                os.remove(images_path + '/facerecognition3.jpg')
                os.remove(images_path + '/facerecognition4.jpg')
                return redirect(url_for('index'))
            else:
                session.pop('_flashes', None)
                flash("Your face has not been recognized, retry!")
                # opnieuw proberen, page refreshen met error message
                return render_template("registerWebcam.html")

        #indien de ogen niet gesloten zijn neem je terug 6 foto's
        else:
            print("eyes not closed")
            session.pop('_flashes', None)
            flash("Your eyes were not closed (enough) on the last picture, please try again!")
            # opnieuw proberen, page refreshen met error message
            return render_template("registerWebcam.html")
    return render_template("registerWebcam.html")


# --UPLOAD PICTURES TO DATABASE--
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        # email wordt via session opgevraagd
        email = session['email']
        images_path = os.path.join('.\dataset', email)
        frame = []
        boxes = []

        # alle foto's in de directory van je account worden eerst verwijderd
        f = glob.glob(os.path.join(images_path, "*"))
        for e in f:
            os.remove(e)

        # foto's worden opgevraagd van Javascript
        img1 = request.files['img1']
        img2 = request.files['img2']
        img3 = request.files['img3']
        img4 = request.files['img4']
        img5 = request.files['img5']
        
        # deze foto's worden opgeslagen
        img1.save('%s/%s' % (images_path, ('%s-1.jpg' % time.strftime("%Y%m%d-%H%M%S"))))
        img2.save('%s/%s' % (images_path, ('%s-2.jpg' % time.strftime("%Y%m%d-%H%M%S"))))
        img3.save('%s/%s' % (images_path, ('%s-3.jpg' % time.strftime("%Y%m%d-%H%M%S"))))
        img4.save('%s/%s' % (images_path, ('%s-4.jpg' % time.strftime("%Y%m%d-%H%M%S"))))
        img5.save('%s/%s' % (images_path, ('%s-5.jpg' % time.strftime("%Y%m%d-%H%M%S"))))
        imgarr = os.listdir(images_path)

        # loop voor deze foto's
        for current in range(len(imgarr)):
            buffer = os.path.join(images_path, imgarr[current])
            # één foto wordt ingelezen met OpenCV2
            frame.append(cv2.imread(buffer))
            # foto wordt zwart wit gemaakt
            gray = cv2.cvtColor(frame[current], cv2.COLOR_BGR2GRAY)
            # gezicht wordt herkend
            boxes.append(classifier.detectMultiScale(gray,
                                                     scaleFactor=1.2,
                                                     minNeighbors=6,
                                                     minSize=(60, 60),
                                                     flags=cv2.CASCADE_SCALE_IMAGE))
            print(boxes[current])

            # nakijken ofdat er een gezicht herkend is
            if len(boxes[current]) == 1:
                for k in boxes[current]:
                    x, y, width, height = k
                    x2, y2 = x + width, y + height
                    # vierkant rond gezicht tekenen
                    cv2.rectangle(gray, (x, y), (x2, y2), (0, 0, 225), 1)
                    # foto resizen naar 128x128
                    crop = cv2.resize(gray[y:y + height, x:x + width], (128, 128))

                # dubbele verificatie dat er een gezicht herkend werd
                # de gezichten vergelijken om in te loggen gebeurd via deze manier dus daarom is dit belangrijk
                try:
                    image_to_be_matched_encoded = face_recognition.face_encodings(frame[current])[0]
                except IndexError as e:
                    print(e)
                    break

                # foto wordt opgeslagen als er een gezicht herkend werd
                cv2.imwrite("./dataset/" + email + "/facerecognition" + str(current) + ".jpg", crop)
            else:
                print('picture ' + str(current+1) + ' failed')

            # delay
            cv2.waitKey(100)

        #deze 6de foto wordt pas na de loop opgeslagen omdat dit de foto is waarbij de ogen toe zijn
        #de foto zal dus niet gebruikt worden om te vergelijken maar als extra safety feature. 
        img6 = request.files['img6']
        img6.save('%s/%s' % (images_path, ("eyes_picture.jpg")))

    return render_template("login.html")


# --LOG-IN WITH WEBCAM--
@app.route('/webcam_login', methods=['GET', 'POST'])
def webcamLogin():
    if request.method == 'POST':
        access = 0
        # delay van 2 seconden om er zeker van te zijn dat foto's correct werden weggeschreven in directory
        time.sleep(2)
        # email uit database halen en opslagen
        email = request.form['email']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM logininfo WHERE email=%s", [email])
        account = cursor.fetchone()

        # nakijken ofdat email in database zit
        if account is not None:
            if account['email'] == email:
                images_path = os.path.join('.\dataset', email)
                print(os.path.exists(images_path + '\login_crop.jpg'))

                # als de login_crop foto niet in de directory zit, dan werd er geen gezicht herkend
                if os.path.exists(images_path + '\login_crop.jpg'):
                    # foto inladen
                    current_picture = face_recognition.load_image_file('./dataset/' + email + '/login.jpg')

                    # nog eens dubbel nakijken ofdat er een gezicht herkend werd
                    if len(current_picture) > 0:
                        # foto encoden en opslagen als dit het geval is
                        current_picture_encoding = face_recognition.face_encodings(current_picture)[0]

                    for file in os.listdir(images_path):
                        # specifieke foto's in directory selecteren waarmee de getrokken foto mee vergeleken moet worden
                        if file.startswith("20"):
                            print(file)
                            # inladen met OpenCV
                            savedpicture = cv2.imread(os.path.join(images_path, file))

                            # nakijken ofdat foto correct is ingeladen
                            if savedpicture.any():
                                # nog eens nakijken of gezicht wordt herkend om errors te vermijden
                                try:
                                    savedpicture_encoding = face_recognition.face_encodings(savedpicture)[0]

                                    # de twee foto's met elkaar vergelijken
                                    results = face_recognition.compare_faces([savedpicture_encoding],
                                                                             current_picture_encoding)
                                    print(results)
                                    if (results[0] == True):
                                        access += 1
                                except IndexError:
                                    # foto verwijderen uit database
                                    os.remove(images_path+'/'+file)

                    # je krijgt alleen toegang tot je account als de meerderheid van je foto's overeenkomen
                    if access > 4:
                         # foto's verwijderen die niet meer gebruikt moeten worden
                        os.remove(images_path + '/login_crop.jpg')
                        os.remove(images_path + '/login.jpg')
                        # doorverwijzen naar profiel want je bent ingelogd!
                        return render_template('profile.html')
                    else:
                        # terugsturen naar de loginpagina want je bent niet ingelogd
                        return render_template('login.html')
                else:
                    # foto's verwijderen die niet meer gebruikt moeten worden
                    os.remove(images_path + '/login.jpg')
                    # error voor als gezicht niet herkend werd
                    session.pop('_flashes', None)
                    flash("Your face has not been recognized, retry!")

                    # terug doorverwijzen naar homepage
                    return redirect(url_for('index'))
        else:
            # error voor als email niet in database te vinden is
            session.pop('_flashes', None)
            flash("Make an account first")

            # terug doorverwijzen naar homepage
            return redirect(url_for('index'))

    return render_template('loginWebcam.html')


# --UPLOAD LOG-IN PICTURE FOR VERIFICATION--
@app.route('/verify', methods=['GET', 'POST'])
def webcamVerify():
    if request.method == 'POST':
        if "email" in request.form:
            # email wordt vanuit Javascript doorgestuurd
            email = request.form['email']
            images_path = os.path.join('.\dataset', email)
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM logininfo WHERE email=%s", [email])
            account = cursor.fetchone()

            # nakijken of account met het emailadres bestaat in de database
            if account is not None:
                if account['email'] == email:
                    # foto opvragen van Javascript
                    img_taken = request.files['image']
                    # foto opslagen in persoonlijke directory
                    img_taken.save(images_path + '/login.jpg')

                    # foto wordt ingeladen met OpenCV
                    frame = cv2.imread(images_path+'/login.jpg')
                    # foto wordt zwart wit gemaakt
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # gezicht wordt herkend
                    boxes = classifier.detectMultiScale(gray,
                                                        scaleFactor=1.2,
                                                        minNeighbors=8,
                                                        minSize=(60, 60),
                                                        flags=cv2.CASCADE_SCALE_IMAGE)
                    print(boxes)

                    # nakijken ofdat er een gezicht herkend is
                    if len(boxes) == 1:
                        for k in boxes:
                            x, y, width, height = k
                            x2, y2 = x + width, y + height
                            # vierkant rond gezicht tekenen
                            cv2.rectangle(frame, (x, y), (x2, y2), (0, 0, 225), 1)
                            # foto resizen naar 128x128
                            crop = cv2.resize(frame[y:y + height, x:x + width], (128, 128))

                            gray = cv2.resize(gray[y:y + height, x:x + width], (128,128))
                            # foto opslagen
                            cv2.imwrite(images_path+'/login_crop.jpg', gray)
                            # delay
                            cv2.waitKey(100)
                    else:
                        if os.path.exists(images_path + '/login_crop.jpg'):
                            # foto verwijderen indien er geen gezicht herkend werd
                            os.remove(images_path + '/login_crop.jpg')
                    session['loginsuccess'] = True

        else:
            # error voor als email niet in database te vinden is
            session.pop('_flashes', None)
            flash("Your email has not been found.")

    return render_template("profile.html")

if __name__ == '__main__':
    app.run(debug=True)
