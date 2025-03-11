from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object("config.Config")
    
    db.init_app(app)
    
    from .routes import main
    app.register_blueprint(main)  # Only one blueprint now

    with app.app_context():
        db.create_all()

    return app
