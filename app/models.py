from . import db

class User(db.Model):
    __tablenme__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    full_name = db.Column(db.String(120))
    password = db.Column(db.String(120))
    gender = db.Column(db.String(50))
    qualification = db.Column(db.String(120))
    dob = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False)
    bio = db.Column(db.String(100))
    scores = db.relationship('Scores', backref='user')

class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(120))
    chapters = db.relationship('Chapter', backref='subject')

class Chapter(db.Model):
    __tablename__ = 'chapter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(120))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    quizzes = db.relationship('Quiz', backref='chapter')

class Quiz(db.Model):
    __tablename__ = 'quiz'
    id = db.Column(db.Integer, primary_key=True)
    quiz_title= db.Column(db.String(80), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'))
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Integer, nullable=False)
    total_questions  = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.String(120))
    scores = db.relationship('Scores', backref='quiz')

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
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))

class Scores(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))    
    time_stamp_of_attempt = db.Column(db.Date, nullable=False)