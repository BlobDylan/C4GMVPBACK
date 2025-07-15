import pytest
import json
from app import db
from app.models import User


class TestSignupRoute:
    """Test cases for signup route."""
    
    def test_successful_signup(self, client):
        """Test successful user signup."""
        response = client.post('/signup', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'phoneNumber': '123-456-7890',
            'role': 'Family Representative'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User created successfully'
        
        # Check user was created in database
        with client.application.app_context():
            user = User.query.filter_by(email='john@example.com').first()
            assert user is not None
            assert user.first_name == 'John'
            assert user.last_name == 'Doe'
            assert user.role == 'Family Representative'
    
    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields."""
        response = client.post('/signup', json={
            'firstName': 'John',
            'lastName': 'Doe'
            # Missing email, password, role
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Missing required fields'
    
    def test_signup_duplicate_email(self, client):
        """Test signup with duplicate email."""
        # Create first user
        client.post('/signup', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'role': 'Family Representative'
        })
        
        # Try to create second user with same email
        response = client.post('/signup', json={
            'firstName': 'Jane',
            'lastName': 'Smith',
            'email': 'john@example.com',
            'password': 'password456',
            'role': 'Guide'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Email already exists'
    
    def test_signup_invalid_role(self, client):
        """Test signup with invalid role."""
        response = client.post('/signup', json={
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john@example.com',
            'password': 'password123',
            'role': 'Invalid Role'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Invalid role'


class TestLoginRoute:
    """Test cases for login route."""
    
    def test_successful_login(self, client, sample_user):
        """Test successful user login."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.commit()
        
        response = client.post('/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['firstName'] == 'Test'
        assert data['user']['lastName'] == 'User'
        assert data['user']['permissions'] == 'user'
        assert data['user']['role'] == 'Family Representative'
    
    def test_login_invalid_email(self, client):
        """Test login with invalid email."""
        response = client.post('/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'Invalid credentials'
    
    def test_login_invalid_password(self, client, sample_user):
        """Test login with invalid password."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.commit()
        
        response = client.post('/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'Invalid credentials'
    
    def test_login_missing_data(self, client):
        """Test login with missing data."""
        response = client.post('/login', json={})
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['message'] == 'Invalid credentials'


class TestLogoutRoute:
    """Test cases for logout route."""
    
    def test_successful_logout(self, client, authenticated_headers):
        """Test successful user logout."""
        response = client.post('/logout', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Successfully logged out'
        
        # Verify token version was incremented
        with client.application.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            assert user.token_version == 1
    
    def test_logout_without_token(self, client):
        """Test logout without authentication token."""
        response = client.post('/logout')
        
        assert response.status_code == 401
    
    def test_logout_with_invalid_token(self, client):
        """Test logout with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.post('/logout', headers=headers)
        
        assert response.status_code == 422  # Unprocessable Entity for invalid JWT