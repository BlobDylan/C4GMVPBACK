import pytest
from app import db
from app.models import User, Event, Registration
from datetime import datetime


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                phone_number="123-456-7890",
                permission_type="user",
                role="Family Representative"
            )
            user.set_password("password123")
            
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.first_name == "John"
            assert user.last_name == "Doe"
            assert user.email == "john@example.com"
            assert user.permission_type == "user"
            assert user.role == "Family Representative"
            assert user.token_version == 0
    
    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                permission_type="user",
                role="Guide"
            )
            user.set_password("password123")
            
            assert user.password_hash is not None
            assert user.password_hash != "password123"
            assert user.check_password("password123") is True
            assert user.check_password("wrongpassword") is False
    
    def test_default_values(self, app):
        """Test default values for user fields."""
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com"
            )
            user.set_password("password123")
            
            db.session.add(user)
            db.session.commit()
            
            assert user.permission_type == "user"
            assert user.role == "Family Representative"
            assert user.token_version == 0


class TestEventModel:
    """Test cases for Event model."""
    
    def test_event_creation(self, app):
        """Test creating a new event."""
        with app.app_context():
            event = Event(
                title="Test Event",
                description="This is a test event",
                date=datetime(2024, 12, 31, 18, 0),
                channel="Hostages Square",
                language="Hebrew",
                location="Jerusalem",
                target_audience="Universities",
                group_size=10,
                num_instructors_needed=2,
                num_representatives_needed=1
            )
            
            db.session.add(event)
            db.session.commit()
            
            assert event.id is not None
            assert event.title == "Test Event"
            assert event.description == "This is a test event"
            assert event.status == "pending"  # default value
            assert event.group_size == 10
            assert event.num_instructors_needed == 2
            assert event.num_representatives_needed == 1
    
    def test_event_default_values(self, app):
        """Test default values for event fields."""
        with app.app_context():
            event = Event(
                title="Test Event",
                description="Test description",
                date=datetime(2024, 12, 31, 18, 0),
                channel="Virtual",
                language="English",
                location="Zoom",
                target_audience="Business Sector"
            )
            
            db.session.add(event)
            db.session.commit()
            
            assert event.status == "pending"
            assert event.group_size == 0
            assert event.num_instructors_needed == 0
            assert event.num_representatives_needed == 0


class TestRegistrationModel:
    """Test cases for Registration model."""
    
    def test_registration_creation(self, app):
        """Test creating a new registration."""
        with app.app_context():
            # Create user and event first
            user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                role="Family Representative"
            )
            user.set_password("password123")
            
            event = Event(
                title="Test Event",
                description="Test description",
                date=datetime(2024, 12, 31, 18, 0),
                channel="Virtual",
                language="English",
                location="Zoom",
                target_audience="Business Sector"
            )
            
            db.session.add(user)
            db.session.add(event)
            db.session.commit()
            
            # Create registration
            registration = Registration(
                user_id=user.id,
                event_id=event.id,
                status="approved"
            )
            
            db.session.add(registration)
            db.session.commit()
            
            assert registration.user_id == user.id
            assert registration.event_id == event.id
            assert registration.status == "approved"
            assert registration.user == user
            assert registration.event == event
    
    def test_registration_default_status(self, app):
        """Test default status for registration."""
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                role="Guide"
            )
            user.set_password("password123")
            
            event = Event(
                title="Test Event",
                description="Test description",
                date=datetime(2024, 12, 31, 18, 0),
                channel="Virtual",
                language="English",
                location="Zoom",
                target_audience="Business Sector"
            )
            
            db.session.add(user)
            db.session.add(event)
            db.session.commit()
            
            registration = Registration(
                user_id=user.id,
                event_id=event.id
            )
            
            db.session.add(registration)
            db.session.commit()
            
            assert registration.status == "approved"  # default value
    
    def test_cascade_deletion(self, app):
        """Test cascade deletion when user or event is deleted."""
        with app.app_context():
            user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                role="Family Representative"
            )
            user.set_password("password123")
            
            event = Event(
                title="Test Event",
                description="Test description",
                date=datetime(2024, 12, 31, 18, 0),
                channel="Virtual",
                language="English",
                location="Zoom",
                target_audience="Business Sector"
            )
            
            db.session.add(user)
            db.session.add(event)
            db.session.commit()
            
            registration = Registration(
                user_id=user.id,
                event_id=event.id
            )
            
            db.session.add(registration)
            db.session.commit()
            
            # Delete user, registration should be deleted too
            db.session.delete(user)
            db.session.commit()
            
            remaining_registration = Registration.query.filter_by(
                user_id=user.id,
                event_id=event.id
            ).first()
            
            assert remaining_registration is None