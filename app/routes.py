from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import User, Subject, Chapter, Quiz, Questions, Scores, db
from .utils import leaderboard
from datetime import datetime
from sqlalchemy import and_, func
import random
import os
import statistics
from functools import wraps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

main = Blueprint("main", __name__)



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("main.login")) 
        return f(*args, **kwargs)
    return decorated_function


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
            return redirect(url_for("main.index"))
        elif user and user.password == password and user.is_admin == True:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("main.admin_dash"))
        else:
            print("invalid credintials")
            return redirect(url_for("main.login"))
        
@main.route("/admin-dashboard", methods=['GET', 'POST'])
@login_required
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
            return redirect(url_for('main.admin_dash'))
        elif form_type=='subject':
            subject_name = request.form['subject_name']
            remarks = request.form['remarks']
            subject = Subject(name=subject_name, description=remarks)
            db.session.add(subject)
            db.session.commit()
            
            return redirect(url_for('main.admin_dash'))
        elif form_type=='search':
            search_query = request.form.get('search', '')
            results = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()
            return render_template("admin-dashboard.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, subjects=results)
        return redirect(url_for('main.admin_dash'))

@main.route("/logout")
def logout():
        session.clear()
        return redirect(url_for("main.index"))

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
        return redirect(url_for("main.login"))
    

@main.route("/admin-dashboard/add-quiz/<int:chapter_id>", methods=["GET", "POST"])
@login_required
def add_quiz(chapter_id):
    if request.method == "GET":
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        return render_template("admin-add-quiz.html", quizzes=quizzes, logged_in=session.get('logged_in'), username=session.get('username'), chapter_id=chapter_id)

@main.route('/new-quiz/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def new_quiz(chapter_id):
    if request.method == 'GET':
        return render_template('new_quiz.html', logged_in=session.get('logged_in'), username=session.get('username'), chapter_id=chapter_id)
    elif request.method == 'POST':
        quiz_title = request.form['quiz_title']
        remarks = request.form['remarks']
        date_of_quiz_str = request.form['date_of_quiz']
        date_of_quiz = datetime.strptime(date_of_quiz_str, "%d-%m-%Y").date()
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
            
            
        quiz = Quiz(quiz_title=quiz_title, chapter_id=chapter_id, remarks=remarks, date_of_quiz=date_of_quiz, time_duration=duration, total_questions=index-1)
        db.session.add(quiz)
        db.session.commit()

    return redirect(url_for('main.add_quiz', chapter_id=chapter_id))

@main.route("/quiz/<quiz_id>", methods=["GET", "POST", "PUT"])
def start_quiz(quiz_id):
    quiz=Quiz.query.filter_by(id=quiz_id).first()
    user = User.query.filter_by(username=session.get('username')).first()
    if request.method == "GET":
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        return render_template("single-quiz.html", questions=questions, quiz=quiz, logged_in=session.get('logged_in'), total_score=None, selected_answer=None, user=user)
    elif request.method == "POST" and request.form.get("_method")=="PUT":
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        quiz_title = request.form.get('quiz_title')
        remarks = request.form.get('remarks')
        date_of_quiz_str = request.form.get('date_of_quiz')
        date_of_quiz = datetime.strptime(date_of_quiz_str, "Date: %Y-%m-%d").date()
        time_duration = int(request.form.get('duration'))
        
        Quiz.query.filter_by(id=int(quiz_id)).update({"quiz_title":quiz_title, "remarks":remarks, "date_of_quiz":date_of_quiz, "time_duration":time_duration})
        db.session.commit()

        index = 1
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
                quiz_id=quiz_id,
                que_no=len(questions) + index
            )

            db.session.add(question)
            index += 1
            Quiz.query.filter_by(id=int(quiz_id)).update({"total_questions":len(questions) + 1})
            db.session.commit()
            
        return redirect(url_for("main.add_quiz", chapter_id=Quiz.query.filter_by(id=quiz_id).first().chapter_id))
    elif request.method == "POST":
        questions = Questions.query.filter_by(quiz_id=quiz_id).all()
        selected_answer = {}
        for question in questions:
            selected_answer[question.que_no] = request.form.get(str(question.que_no)+"choice")
        # print(selected_answer)-+
        total_score = 0
        for answer in selected_answer:
            
            if selected_answer[answer] == Questions.query.filter(and_(Questions.que_no==answer, Questions.quiz_id==quiz_id)).first().correct_answer:
                total_score += 1
        score = Scores(user_id=user.id, quiz_id=quiz_id, total_score=total_score*10, time_stamp_of_attempt=datetime.now())
        db.session.add(score)
        db.session.commit()
       

        return render_template('single-quiz.html', questions=questions, quiz=quiz, logged_in=session.get('logged_in'),quiz_id=quiz_id, total_score=total_score*10, submitted=True, selected_answer=selected_answer, user=user)
@main.route("/all-quiz", methods=["GET", "POST"])
def quiz():
    if session.get('logged_in'):
        user = User.query.filter_by(username=session.get('username')).first()    
    else:
        user = None
    all_quizzes = Quiz.query.all()
    
    if request.method == "GET":
        return render_template("quiz.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, all_quizzes=all_quizzes)
    elif request.method == "POST":
        search_query = request.form.get('search', '')
        results = Quiz.query.filter(Quiz.quiz_title.ilike(f'%{search_query}%')).all()
        
        return render_template("quiz.html", logged_in=session.get('logged_in'), username=session.get('username'), current_user=user, all_quizzes=results)
    

@main.route("/profile/<name>")
@main.route("/profile")
def profile(name=""):
    if session.get('logged_in') and name=="":
        user = User.query.filter_by(username=session.get('username')).first()
    elif name!="":
        user = User.query.filter_by(full_name=name).first()
    else:
        user = None
    quiz = []
    for i in user.scores:
        quiz.append(Quiz.query.filter_by(id=i.quiz_id).first())
    labels = []
    sizes = []
    score = db.session.query(Scores.quiz_id, func.sum(Scores.total_score)).filter(Scores.user_id == user.id).group_by(Scores.quiz_id).all()
    
    
    scores_table = {'quiz_title':[], 'Marks':[], 'Time':[]}
    if score:
        for i in score:
            
            labels.append(quiz[i[0]-1].quiz_title)
            
            sizes.append(i[1])
        colors = [f'#{random.randint(0, 0xFFFFFF):06x}' for _ in sizes]
        explode = [0.1 if size == max(sizes) else 0 for size in sizes]

        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', explode=explode, shadow=True, startangle=140)
        if os.path.exists("app/static/images/piechart.png"):
            os.remove("app/static/images/piechart.png")
            plt.clf()
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', explode=explode, shadow=True, startangle=140)
            plt.savefig("app/static/images/piechart.png")
        else:
            plt.savefig("app/static/images/piechart.png") 
            
        print(labels, sizes)
        for i in user.scores:
            scores_table['quiz_title'].append(Quiz.query.filter_by(id=i.quiz_id).first().quiz_title)
            scores_table['Marks'].append(str(i.total_score))
            scores_table['Time'].append(str(i.time_stamp_of_attempt))
    return render_template("profile.html", logged_in=session.get('logged_in'), username=session.get('username'), leaderboard_user=user, user=user, name=name, quiz=quiz, scores_table=scores_table)

@main.route('/delete-subject/<int:subject_id>')
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('main.admin_dash'))

@main.route('/delete-chapter/<int:chapter_id>')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('main.admin_dash'))

@main.route('/summary')
@login_required
def summary():
    if session.get('logged_in'):
        users = User.query.all()
        scores = Scores.query.all()
        values = []
        for i in scores:
            values.append(i.quiz_id)
        mode_value = statistics.mode(values)
        most_popular_quiz = Quiz.query.filter_by(id=mode_value).first()
        results = (db.session.query(Chapter.name, db.func.count(Scores.id)).join(Quiz, Chapter.id == Quiz.chapter_id).join(Scores, Quiz.id == Scores.quiz_id).group_by(Chapter.id).all())
        chapter_names = [r[0] for r in results]
        attempt_counts = [r[1] for r in results]


        plt.figure(figsize=(10, 6))

        plt.bar(chapter_names, attempt_counts, color='skyblue')
        plt.xlabel("Chapters")
        plt.ylabel("Quiz Attempts")
        plt.title("Quiz Attempt Frequency by Chapter")
        if os.path.exists("app/static/images/barchart.png"):
            os.remove("app/static/images/barchart.png")
            plt.clf()
            plt.bar(chapter_names, attempt_counts, color='skyblue')
            plt.savefig("app/static/images/barchart.png")
        else:
            plt.savefig("app/static/images/barchart.png")
        plt.clf()
        return render_template('summary.html', logged_in=session.get('logged_in'), username=session.get('username'), users=users, scores=scores, most_popular_quiz=most_popular_quiz)