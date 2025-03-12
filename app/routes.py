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
    

@main.route("/admin-dashboard/add-quiz/<int:chapter_id>", methods=["GET", "POST"])
def add_quiz(chapter_id):
    if request.method == "GET":
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return render_template("admin-add-quiz.html", quizzes=quizzes, logged_in=session.get('logged_in'), username=session.get('username'), chapter_id=chapter_id)

@main.route('/new-quiz/<int:chapter_id>', methods=['GET', 'POST'])
def new_quiz(chapter_id):
    if request.method == 'GET':
        return render_template('new_quiz.html', logged_in=session.get('logged_in'), username=session.get('username'), chapter_id=chapter_id)
    elif request.method == 'POST':
        quiz_title = request.form['quiz_title']
        remarks = request.form['remarks']
        date_of_quiz_str = request.form['date_of_quiz']
        date_of_quiz = datetime.strptime(date_of_quiz_str, "%Y-%m-%d").date()
        duration = request.form['duration']
        index = 1
        quiz_id = len(Quiz.query.all()) + 1
        while f"new_question_{index}" in request.form:
            new_question = request.form[f'new_question_{index}']
            option1 = request.form[f'option1_{index}']
            option2 = request.form[f'option2_{index}']
            option3 = request.form[f'option3_{index}']
            option4 = request.form[f'option4_{index}']
            correct_answer_index = request.form.get(f'correct_option_{index}')

            if correct_answer_index == "1":
                correct_answer = option1
            elif correct_answer_index == "2":
                correct_answer = option2
            elif correct_answer_index == "3":
                correct_answer = option3
            elif correct_answer_index == "4":
                correct_answer = option4
            else:
                correct_answer = ""

            question = Questions(
                question=new_question,
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4,
                correct_answer=correct_answer,
                que_no=+ index,
                quiz_id=quiz_id
            )

            db.session.add(question)
            index += 1
            
            
        quiz = Quiz(quiz_title=quiz_title, chapter_id=chapter_id, remarks=remarks, date_of_quiz=date_of_quiz, time_duration=duration, total_questions=index)
        db.session.add(quiz)
        db.session.commit()

    return redirect(url_for('add_quiz', chapter_id=chapter_id))
