import os
from flask import Flask, render_template, request, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, current_user, login_required

from models import User

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app, db, bcrypt):
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = 'I LOVE TANISHA'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            hashed_password = bcrypt.generate_password_hash(password)

            user = User(username=username, password=hashed_password)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for('index'))


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter(User.username == username).first()

            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('fillup', username=user.username))
            else:
                return "Failed to login"

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/fillup/', methods=['GET','POST'])
    @login_required
    def fillup():
        if request.method == 'POST':
            photo = request.files.get('userimg')
            username = request.form.get('username')
            userphn = request.form.get('userphn')
            useremail = request.form.get('useremail')
            objective = request.form.get('objective')

            clgname = request.form.get('clgname')
            degree = request.form.get('degree')
            duration = request.form.get('duration')
            marks = request.form.get('marks')
            userskill = request.form.getlist('userskill[]')
            workexp = request.form.getlist('workexp[]')
            userproj = request.form.getlist('userproj[]')
            usercert = request.form.getlist('usercert[]')

            photo_url = None

            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                photo.save(photo_path)

                photo_url = url_for('static', filename=f'uploads/{filename}')

            session['username'] = username
            session['userphn'] = userphn
            session['useremail'] = useremail
            session['objective'] = objective
            session['photo_url'] = photo_url
            session['clgname'] = clgname
            session['degree'] = degree
            session['duration'] = duration
            session['marks'] = marks
            session['userskill'] = userskill
            session['workexp'] = workexp
            session['userproj'] = userproj
            session['usercert'] = usercert

            return redirect(url_for('resume', username=username))

        return render_template('resume_fill.html')

    @app.route('/resume/<username>', methods=['GET'])
    def resume(username):
        if session.get('username') != username:
            return "Unauthorized", 403

        name = session.get('username')
        phn = session.get('userphn')
        uemail = session.get('useremail')
        objective = session.get('objective')
        photo_url = session.get('photo_url')

        clname = session.get('clgname')
        dgr = session.get('degree')
        durn = session.get('duration')
        mrks = session.get('marks')
        skills = session.get('userskill', [])
        wexps = session.get('workexp', [])
        prjs = session.get('userproj', [])
        crfs = session.get('usercert', [])

        print(f"Session data retrieved: {session}")
        return render_template('resume.html', photo_url=photo_url, name=name, phn=phn, uemail=uemail, objective=objective, clname=clname, dgr=dgr, durn=durn, mrks=mrks, skills=skills, wexps=wexps, prjs=prjs, crfs=crfs)

