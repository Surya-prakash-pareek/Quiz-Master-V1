from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import User, Subject, Chapter, Quiz, Questions, Scores, db
from .utils import leaderboard
from datetime import datetime
import random
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

main = Blueprint("main", __name__)

@main.route("/")
def index():
    user = None
    if session.get('logged_in'):
        user = User.query.filter_by(username=session.get('username')).first()
    return render_template("index.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, leaderboard=leaderboard())

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        print(user)
        if user and user.password == password and user.is_admin == False:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("index"))
        elif user and user.password == password and user.is_admin == True:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("admin_dash"))
        else:
            print("invalid credintials")
            return redirect(url_for("login"))
        
@main.route("/admin-dashboard", methods=['GET', 'POST'])
def admin_dash():
    subjects = Subject.query.all()
    user = User.query.filter_by(username=session.get('username')).first()
    if request.method=='GET':
        if session.get('logged_in'):
            user = User.query.filter_by(username=session.get('username')).first()
        else:
            user = None
        return render_template("admin-dashboard.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, subjects=subjects)
    elif request.method=='POST':
        form_type = request.form.get('form_type')
        if form_type=='chapter':
            chapter_name = request.form['chapter_name']
            subject_id = request.form['subid']
            chap_desc = request.form['chap_desc']
            chapter = Chapter(name=chapter_name, subject_id=subject_id, description=chap_desc)
            db.session.add(chapter)
            db.session.commit()
            return render_template("admin-dashboard.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, subjects=subjects)
        elif form_type=='subject':
            subject_name = request.form['subject_name']
            remarks = request.form['remarks']
            subject = Subject(name=subject_name, description=remarks)
            db.session.add(subject)
            db.session.commit()
            return render_template("admin-dashboard.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, subjects=subjects)
        elif form_type=='search':
            search_query = request.form.get('search', '')
            results = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()
            return render_template("admin-dashboard.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, subjects=results)
        return render_template("admin-dashboard.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, subjects=subjects)

@main.route("/logout")
def logout():
        session.clear()
        return redirect(url_for("index"))

@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['fullname']
        dob = request.form['dob']
        gender = request.form['gender']
        qualification = request.form['qualification']
        user = User(username=username, password=password, full_name=full_name, dob=dob, qualification=qualification, gender=gender)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))