from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(50))
    qualification = db.Column(db.String(120))
    dob = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String(100))
    scores = db.relationship('Scores', backref='user', cascade="all, delete-orphan")

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(120))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id', ondelete="CASCADE"), nullable=False)
    
    quizzes = db.relationship('Quiz', backref='chapter', cascade="all, delete-orphan")

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    quiz_title = db.Column(db.String(80), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete="CASCADE"), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.String(120))
    
    scores = db.relationship('Scores', backref='quiz', cascade="all, delete-orphan")
    questions = db.relationship('Questions', backref='quiz', cascade="all, delete-orphan")

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120), nullable=False)
    que_no = db.Column(db.Integer, nullable=False)
    option1 = db.Column(db.String(120), nullable=False)
    option2 = db.Column(db.String(120), nullable=False)
    option3 = db.Column(db.String(120), nullable=False)
    option4 = db.Column(db.String(120), nullable=False)
    correct_answer = db.Column(db.String(120), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)

class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"), nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
