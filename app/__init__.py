from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import event
from sqlite3 import Connection as SQLiteConnection
from sqlalchemy.engine import Engine
from flask_cors import CORS
from dotenv import load_dotenv
import os

db = SQLAlchemy()
jwt = JWTManager()


def create_super_admin_if_not_exists():
    from .models import User

    super_admin_email = os.getenv("SUPER_ADMIN_EMAIL")
    super_admin_password = os.getenv("SUPER_ADMIN_PASSWORD")

    if not super_admin_email or not super_admin_password:
        print(
            "SUPER_ADMIN_EMAIL or SUPER_ADMIN_PASSWORD not set in .env. Skipping super admin creation."
        )
        return

    existing_super_admin = User.query.filter_by(email=super_admin_email).first()

    if not existing_super_admin:
        print(f"Creating super admin: {super_admin_email}")
        super_admin = User(
            first_name="Super",
            last_name="Admin",
            email=super_admin_email,
            phone_number="N/A",
            permission_type="super_admin",
        )
        super_admin.set_password(super_admin_password)
        db.session.add(super_admin)
        try:
            db.session.commit()
            print(f"Super admin '{super_admin_email}' created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating super admin: {str(e)}")
    elif existing_super_admin.permission_type != "super_admin":
        print(f"User '{super_admin_email}' exists, updating to super_admin.")
        existing_super_admin.permission_type = "super_admin"
        try:
            db.session.commit()
            print(f"User '{super_admin_email}' updated to super_admin successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user '{super_admin_email}' to super_admin: {str(e)}")
    else:
        print(f"Super admin '{super_admin_email}' already exists.")


def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, SQLiteConnection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    db.init_app(app)
    jwt.init_app(app)

    @app.route("/")
    def home():
        return {"message": "API is up and running 🎉"}

    with app.app_context():
        from .models import User, Event, Registration
        from .routes import auth, user, admin, events

        app.register_blueprint(auth.bp)
        app.register_blueprint(user.bp)
        app.register_blueprint(admin.bp)
        app.register_blueprint(events.bp)

        db.create_all()
        create_super_admin_if_not_exists()

    return app
