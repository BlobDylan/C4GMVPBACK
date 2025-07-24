from . import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(128), nullable=False)
    token_version = db.Column(db.Integer, default=0)
    permission_type = db.Column(db.String(20), nullable=False, default="user")
    preferredLanguages = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(50), nullable=False, default="Family Representative")

    registrations = db.relationship(
        "Registration",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    channel = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    group_size = db.Column(db.Integer, nullable=False, default=0)
    num_instructors_needed = db.Column(db.Integer, nullable=False, default=0)
    num_representatives_needed = db.Column(db.Integer, nullable=False, default=0)
    target_audience = db.Column(db.String(50), nullable=False)
    group_description = db.Column(db.Text, nullable=True)
    additional_notes = db.Column(db.Text, nullable=True)
    contact_phone_number = db.Column(db.String(20), nullable=True)

    registrations = db.relationship(
        "Registration",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Registration(db.Model):
    __tablename__ = "registrations"
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    event_id = db.Column(
        db.Integer, db.ForeignKey("event.id", ondelete="CASCADE"), primary_key=True
    )
    status = db.Column(db.String(20), nullable=False, default="approved")

    user = db.relationship("User", back_populates="registrations")
    event = db.relationship("Event", back_populates="registrations")
