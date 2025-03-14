from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.utils import create_admin

db = SQLAlchemy()



def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config.from_object("config.Config")
    
    db.init_app(app)
    from .routes import main
    app.register_blueprint(main)  

    with app.app_context():
        db.create_all()
        create_admin()
   
    return app
