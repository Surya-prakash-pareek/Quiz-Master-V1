from flask_login import UserMixin

def leaderboard():
    from .models import User, Scores, db
    return db.session.query(
        User.full_name, db.func.sum(Scores.total_score).label('total_score')
    ).join(Scores, Scores.user_id == User.id).group_by(Scores.user_id).order_by(db.func.sum(Scores.total_score).desc()).all()

def create_admin():
    from .models import User, db
    if not User.query.filter_by(username='admin@gmail.com').first():
        admin = User(username='admin@gmail.com', password='admin123', is_admin=True, full_name="Quiz Master")
        db.session.add(admin)
        db.session.commit()



