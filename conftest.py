import pytest
import os
from app import create_app, db
from app.models import User, Event, Registration
from datetime import datetime


@pytest.fixture
def app():
    """Create application for the tests."""
    # Set test configuration
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
    os.environ['FLASK_ENV'] = 'testing'
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        phone_number="123-456-7890",
        permission_type="user",
        role="Family Representative"
    )
    user.set_password("password123")
    return user


@pytest.fixture
def sample_admin():
    """Create a sample admin user for testing."""
    admin = User(
        first_name="Admin",
        last_name="User",
        email="admin@example.com",
        phone_number="123-456-7891",
        permission_type="admin",
        role="Guide"
    )
    admin.set_password("admin123")
    return admin


@pytest.fixture
def sample_super_admin():
    """Create a sample super admin user for testing."""
    super_admin = User(
        first_name="Super",
        last_name="Admin",
        email="superadmin@example.com",
        phone_number="123-456-7892",
        permission_type="super_admin",
        role="Guide"
    )
    super_admin.set_password("superadmin123")
    return super_admin


@pytest.fixture
def sample_event():
    """Create a sample event for testing."""
    return Event(
        title="Test Event",
        description="This is a test event",
        date=datetime(2024, 12, 31, 18, 0),
        channel="Hostages Square",
        language="Hebrew",
        location="Jerusalem",
        status="pending",
        group_size=10,
        num_instructors_needed=2,
        num_representatives_needed=1,
        target_audience="Universities",
        group_description="Test group",
        additional_notes="Test notes"
    )


@pytest.fixture
def authenticated_headers(client, sample_user):
    """Get authentication headers for a regular user."""
    with client.application.app_context():
        db.session.add(sample_user)
        db.session.commit()
        
        response = client.post('/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client, sample_admin):
    """Get authentication headers for an admin user."""
    with client.application.app_context():
        db.session.add(sample_admin)
        db.session.commit()
        
        response = client.post('/login', json={
            'email': 'admin@example.com',
            'password': 'admin123'
        })
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def super_admin_headers(client, sample_super_admin):
    """Get authentication headers for a super admin user."""
    with client.application.app_context():
        db.session.add(sample_super_admin)
        db.session.commit()
        
        response = client.post('/login', json={
            'email': 'superadmin@example.com',
            'password': 'superadmin123'
        })
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}