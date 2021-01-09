# misc
import os
import sys
import itertools
import math
# image and text
import pyautogui as auto
from PIL import Image
from pytesseract import image_to_string
import re
# time
import time
from datetime import datetime, timedelta
import dateutil
import atexit
# flask + sql
from flask import Flask, render_template, url_for, request, redirect, flash,\
    get_flashed_messages, session, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Float, String, DateTime, Interval, select, ForeignKey, Date, cast
from sqlalchemy.orm import relationship
import sqlite3
# np, pd
import numpy as np
import pandas as pd
# forms
from flask_login import login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import Form, TextField, PasswordField, SelectField, validators
from werkzeug.security import check_password_hash, generate_password_hash
import pytz
import universities

# .\env\Scripts\activate.bat
# create app, db
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['SECRET_KEY'] = 'soomztudy202022021'
db = SQLAlchemy(app=app) # create database

# for heroku
os.environ['DISPLAY'] = ':0'

# define database tables
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    timezone = db.Column(db.String(200))
    university = db.Column(db.String(400))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    children = relationship("Classes")

class Classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.Integer, ForeignKey('users.id'))
    class_name = db.Column(db.String(200), nullable=False)
    subject_area = db.Column(db.String(200), nullable=False)
    class_start = db.Column(db.DateTime,nullable=False)
    class_end = db.Column(db.DateTime,nullable=False)
    class_length = db.Column(db.Integer,nullable=False)
    class_size = db.Column(db.Integer,nullable=False)
    prof = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    children = relationship("Events")

class Events(db.Model):
    __tablename__ = 'events'
    log_id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.Integer, ForeignKey('users.id'))
    class_id = db.Column(db.Integer, ForeignKey('classes.id'))
    ptcpt_num = db.Column(db.Integer(),nullable=False)
    ptcpt_pct = db.Column(db.Float(),nullable=False)
    avg_ptcpt_pct = db.Column(db.Float(),nullable=False)
    time_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_created = db.Column(db.Date, default=datetime.today)

# main fn

# configure directory
filename = 'static/images/curr_part.png'
# os.chdir(dname) # change dir to this file dir
def get_num(class_size=0,class_id=0):
    '''
    get number of participants in zoom
    '''
    print("current time: ", time.strftime("%H:%M:%S", time.localtime(time.time())))
    try:
        gn_start_time = datetime.now()
        loc = auto.locateOnScreen('static/images/parts.png')#,confidence=0.5) # left, top, width, height
        loc = list(loc)
        # print('Participants found')
        # increase width and height to incude number of participants and increase res for tesseract
        loc[0] = loc[0] - 30
        loc[1] = loc[1] - 10
        loc[2] = loc[2] * 2 
        loc[3] = loc[3] * 2
        # take screenshot
        auto.screenshot(filename,region=loc)
        # print('Screenshot taken')
        # read text from image and get number
        text = image_to_string(Image.open(filename))
        text = text.replace(' ','').replace('\n','')
        p = re.compile(r'Participants\((\d+)')
        num_part = p.match(text).group(1) # number
        print("Number of participants", num_part)
        
        # save num part into event table
        ptcpt_num = int(num_part)
        ptcpt_pct = ptcpt_num/int(class_size)
        avg_ptcpt_pct = ptcpt_pct

        # ideally want to pass in as batch
        new_event = Events(uid=session['uid'], class_id=class_id, ptcpt_num=ptcpt_num, ptcpt_pct=ptcpt_pct, avg_ptcpt_pct=avg_ptcpt_pct)
        db.session.add(new_event)
        db.session.commit()

    except Exception as e:
        # print(e)
        print("Participants not found")
    # print("fn took ", time.time() - start_time, " to run")
    return datetime.now() - gn_start_time

# main page
@app.route('/',methods=['POST','GET'])
def index():
    # global track_time_start
    # track_time_start = time.time()
    im = ["instr_slide1.png","instr_slide2.png","instr_slide3.png","instr_slide4.png"]
    tut_im = ["/static/images/" + i for i in im]
    # print(tut_im)
    # logged in
    if 'logged_in' in session and 'username' in session:
        # username='tyler'
        # uid=1
        username = session['username']
        uid = session['uid']
        r = db.engine.execute('select * from Classes where uid="%s"' % uid)
        classes = []
        for c in r:
            classes.append(c['class_name'])
        # print(classes)
    # not logged in
    else:
        classes = False
        session['logged_in'] = False
        uid = 999
        username = 'notloggedin'
    try:
        if request.method == "POST":
            '''
            get num every 60 seconds until the desired time is reached
            '''
            # track_time_start = time.time()
            if session['logged_in'] == True:
                # get class name from select
                trk_class = request.form.get("class_select")
                # and class size from db
                r = db.engine.execute('select class_size, id from classes where uid=? and class_name=?',uid,trk_class)
                for i in r:
                    class_size = i.class_size
                    class_id = i.id
                    
            else:
                # get class name from text input
                trk_class = request.form.get("class_text")
                # and class size from text input
                class_size = request.form.get("class_size")
                class_id = 999
            # print('class_size',class_size)
            trk_until_h = request.form.get("track_until_hrs")
            trk_until_m = request.form.get("track_until_mins")
            trk_length = int(trk_until_h) * 3600 + int(trk_until_m) * 60
            print(uid, trk_class)
            # define globals for scheduler
            global first_secs
            first_secs = 300 # first 5 min
            global last_secs
            last_secs = 300
            global start_time
            start_time = datetime.now()
            global end_time
            join_time = start_time + timedelta(seconds=first_secs)
            end_time = start_time + timedelta(seconds=trk_length)
            # end_time = start_time + timedelta(seconds=2)
            leave_time = end_time - timedelta(seconds=last_secs)
            print("start time: ",start_time.strftime("%I:%M:%S %p"), "end time: ", end_time.strftime("%I:%M:%S %p"))
            if end_time < join_time:
                join_time = end_time
            if end_time < leave_time:
                leave_time = end_time
            print("join time: ",join_time.strftime("%I:%M:%S %p"), "leave time: ", leave_time.strftime("%I:%M:%S %p"))
            short_int = 2
            long_int = 30
            if trk_length <= 600: # for short classes, just check on short int.
                long_int = short_int

            # run tracking
            while datetime.now() < join_time:
                run_time = get_num(class_size,class_id).total_seconds()
                diff = short_int - run_time
                if diff < 0:
                    time.sleep(short_int+diff % short_int) # run at next int if skipped one
                else:
                    time.sleep(diff)
                # run_get_num(short_int,class_size)
            while datetime.now() < leave_time:
                run_time = get_num(class_size,class_id).total_seconds()
                diff = long_int - run_time
                if diff < 0:
                    time.sleep(long_int+diff % long_int) # run at immediate next int
                else:
                    time.sleep(diff)
                # run_get_num(long_int,class_size)
            while datetime.now() < end_time:
                run_time = get_num(class_size,class_id).total_seconds()
                diff = short_int - run_time
                if diff < 0:
                    time.sleep(short_int+diff % short_int) # run at immediate next int
                else:
                    time.sleep(diff)
            # finally recalculate avg percent participation for session 
            # r = db.engine.execute('SELECT uid, class_id, date_created, avg(ptcpt_pct) AS avg FROM Events GROUP BY uid, class_id, date_created;')
            uid = session['uid']
            cid = class_id
            dt_crt = str(datetime.today()).split()[0]
            # print(uid,cid,type(dt_crt),dt_crt)
            sql_cmd = f"SELECT uid, class_id, date_created, avg(ptcpt_pct) AS avg FROM Events WHERE uid={uid} AND class_id={cid} AND date_created='{dt_crt}'"
            r = db.engine.execute(sql_cmd)
            for i in r:
                # print(i)
                uid = i[0]
                cid = i[1]
                date = i[2]
                avg = i[3]
                sql_cmd = f"UPDATE Events SET avg_ptcpt_pct={avg} WHERE uid={uid} AND class_id={cid} AND date_created='{dt_crt}'"
                u = db.engine.execute(sql_cmd)
            return render_template('index.html', loggedIn = session['logged_in'],classes=classes, tut_list=tut_im,status="Done!")
    except Exception as e:
        return(str(e))
    return render_template('index.html', loggedIn = session['logged_in'],classes=classes, tut_list=tut_im,status="Not")

# registration page
class RegistrationForm(Form): # inherit from wtform.Form
    username = TextField('Username',[validators.Length(min=4,max=50)])
    password = PasswordField('Password',[validators.DataRequired(),
                                        validators.EqualTo('confirm',message='Passwords do not match.')]
                            )
    confirm = PasswordField('Repeat Password')
    tzs = pytz.common_timezones
    tzs.append('NA')
    timezone = SelectField(label = 'Timezone(optional)',choices = tzs,default="NA")
    unis1 = [uni.name for uni in universities.API().search(country = "United States")]
    unis2 = [uni.name for uni in universities.API().search(country = "Canada")]
    unis = sorted(unis1 + unis2)
    unis.append('NA')
    university = SelectField(label = 'University(optional)',choices = unis,default="NA")

@app.route('/register/', methods=['POST','GET'])
def register():
    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            password = generate_password_hash(form.password.data, method = 'sha256')
            timezone = form.timezone.data
            university = form.university.data
            new_register = Users(username=username, password=password, timezone=timezone, university=university)
            # if un alr exists
            exists = db.session.query(Users).filter_by(username=username)
            if exists.count() > 0:
                flash("The username '" + username +"' is already taken. Please choose another.")
                return redirect(url_for('register'))
            # else successful signup
            else:
                db.session.add(new_register)
                db.session.commit()
                session['logged_in'] = True
                session['username'] = username
                r = db.engine.execute('select id from Users where username="%s"' % username)
                for uid in r:
                     session['uid'] = uid['id']
                flash("Thanks for registering, " + session['username'] +"!")
                return redirect(url_for('index'))
    except Exception as e:
        return(str(e))
    return render_template('register.html',form=form)

# login page
class LoginForm(Form): # inherit from wtform.Form
    username = TextField('Username',[validators.Length(min=4,max=50)])
    password = PasswordField('Password',[validators.DataRequired()])

@app.route('/login/', methods=['POST','GET'])
def login():
    try:
        form = LoginForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            password = form.password.data
            r = db.engine.execute('select * from Users where username="%s"' % username)
            rr = len(r.fetchall())
            # incorrect un
            if rr == 0:
                flash("Username does not exist")
                return render_template('login.html',form=form)
            # un matches
            else:
                r = db.engine.execute('select * from Users where username="%s"' % username)
                for i in r:
                    hashed_pass = i[2]
                    # check pw matches
                    if check_password_hash(hashed_pass,password):
                        session['logged_in'] = True
                        session['username'] = username
                        r = db.engine.execute('select id from Users where username="%s"' % username)
                        for uid in r:
                            # print(uid['id'])
                            session['uid'] = uid['id']
                        flash("Successful login. Welcome " + session['username'] + "!")
                        return redirect(url_for('index'))
                    # else incorrect
                    else:
                        flash("Incorrect username or password")
                        return redirect(url_for('login',form=form))
    except Exception as e:
        return(str(e))
    return render_template('login.html',form=form)

@app.route('/logout/')
def logout():
    session['logged_in'] = False
    session['username'] = None
    session['uid'] = None
    flash("You have been logged out")
    return redirect(url_for('index'))

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = dateutil.parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%H:%M'
    return native.strftime(format) 

@app.route('/edit_classes/', methods=['POST','GET'])
def edit_classes():
    session["logged_in"] = True
    uid = session['uid']
    try:
        if request.method == "POST":
            class_names = request.form.getlist("classNames[]")
            class_sizes = request.form.getlist("classSizes[]")
            start_times = request.form.getlist("startTimes[]")
            end_times = request.form.getlist("endTimes[]")
            class_lengths = request.form.getlist("classLengths[]")
            subjects = request.form.getlist("subjects[]")
            PERs = request.form.getlist("PERs[]")
            new_classes = np.column_stack((class_names, class_sizes, start_times,
                                           end_times,class_lengths,subjects,PERs))
            new_classes_df = pd.DataFrame(new_classes,columns=["class_names","class_sizes",
            "start_times","end_times","class_lengths","subjects","PERs"])
            # clear old classes
            db.engine.execute('delete from Classes where uid="%i"' % int(uid))
            # add new classes
            for i,c in new_classes_df.iterrows():
                et_str = c["end_times"]
                st_str = c["start_times"]
                et = datetime.strptime(et_str, '%H:%M')
                st = datetime.strptime(st_str, '%H:%M')
                new_class = Classes(uid=uid, class_name=c["class_names"], subject_area=c["subjects"],
                class_start=st,class_end=et,class_length=c["class_lengths"],class_size=c["class_sizes"],prof=c["PERs"])
                db.session.add(new_class)
                db.session.commit()

    except Exception as e:
        return(str(e))
    # load preexisting classes into classes
    pre_classes =  db.engine.execute('select * from Classes where uid="%i"' % int(uid))
    # for c in pre_classes:
    #     print(c.class_name)
    return render_template('edit_classes.html',loggedIn = session['logged_in'],classes=pre_classes)

@app.route('/view_graphs/')
def view_graphs():
    return render_template('view_graphs.html',loggedIn = session['logged_in'])

@app.route('/my_graphs/')
def my_graphs():
    return render_template('my_graphs.html',loggedIn = session['logged_in'])

@app.route('/check_visible/',methods = ['GET','POST'])
def checkVisible():
    print("here")
    max_count = 0
    while max_count < 3:
        if auto.locateOnScreen('static/images/parts.png'):#,confidence=0.5): # left, top, width, height
            print("found")
            return jsonify("found")
        else:
            print("not found")
            time.sleep(1)
        max_count = max_count + 1
    return jsonify("not found")

if __name__ == '__main__':
 app.run(debug=True)