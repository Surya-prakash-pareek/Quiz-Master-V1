from flask import Blueprint, render_template, request, redirect, url_for, session
from .models import User, Subject, Chapter, Quiz, Questions, Scores, db

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

