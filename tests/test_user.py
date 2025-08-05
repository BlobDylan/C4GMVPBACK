import pytest
import json
from app import db
from app.models import User, Event, Registration
from datetime import datetime


class TestGetCurrentUser:
    """Test cases for /me route."""
    
    def test_get_current_user_success(self, client, authenticated_headers, sample_user):
        """Test getting current user info with valid token."""
        response = client.get('/me', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == sample_user.email
        assert data['firstName'] == 'Test'
        assert data['lastName'] == 'User'
        assert data['permissions'] == 'user'
        assert data['role'] == 'Family Representative'
    
    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get('/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/me', headers=headers)
        
        assert response.status_code == 422


class TestRegisterForEvent:
    """Test cases for event registration."""
    
    def test_register_for_event_success(self, client, authenticated_headers, sample_event, sample_user):
        """Test successful event registration."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.post(f'/events/{event_id}/register', headers=authenticated_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Registered successfully'
        assert data['status'] == 'approved'  # Family Representative gets approved
        
        # Check registration was created in database
        with client.application.app_context():
            user = User.query.filter_by(email=sample_user.email).first()
            registration = Registration.query.filter_by(
                user_id=user.id,
                event_id=event_id
            ).first()
            assert registration is not None
            assert registration.status == 'approved'
    
    def test_register_for_event_guide_pending(self, client, sample_event):
        """Test Guide registration gets pending status."""
        with client.application.app_context():
            # Create a guide user
            guide = User(
                first_name="Guide",
                last_name="User",
                email="guide@example.com",
                role="Guide"
            )
            guide.set_password("password123")
            db.session.add(guide)
            db.session.add(sample_event)
            db.session.commit()
            
            # Login as guide
            login_response = client.post('/login', json={
                'email': 'guide@example.com',
                'password': 'password123'
            })
            token = login_response.json['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            event_id = sample_event.id
        
        response = client.post(f'/events/{event_id}/register', headers=headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Registered successfully'
        assert data['status'] == 'pending'  # Guide gets pending status
    
    def test_register_for_nonexistent_event(self, client, authenticated_headers):
        """Test registration for non-existent event."""
        response = client.post('/events/999/register', headers=authenticated_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'Event not found'
    
    def test_register_for_event_already_registered(self, client, authenticated_headers, sample_event):
        """Test registration when already registered."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        # First registration
        client.post(f'/events/{event_id}/register', headers=authenticated_headers)
        
        # Second registration attempt
        response = client.post(f'/events/{event_id}/register', headers=authenticated_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Already registered'
    
    def test_register_unauthorized(self, client, sample_event):
        """Test registration without authentication."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.post(f'/events/{event_id}/register')
        
        assert response.status_code == 401


class TestUnregisterFromEvent:
    """Test cases for event unregistration."""
    
    def test_unregister_from_event_success(self, client, authenticated_headers, sample_event, sample_user):
        """Test successful event unregistration."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        # First register
        client.post(f'/events/{event_id}/register', headers=authenticated_headers)
        
        # Then unregister
        response = client.delete(f'/events/{event_id}/unregister', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Unregistered successfully'
        
        # Check registration was removed from database
        with client.application.app_context():
            user = User.query.filter_by(email=sample_user.email).first()
            registration = Registration.query.filter_by(
                user_id=user.id,
                event_id=event_id
            ).first()
            assert registration is None
    
    def test_unregister_not_registered(self, client, authenticated_headers, sample_event):
        """Test unregistration when not registered."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.delete(f'/events/{event_id}/unregister', headers=authenticated_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'Not registered'
    
    def test_unregister_unauthorized(self, client, sample_event):
        """Test unregistration without authentication."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.delete(f'/events/{event_id}/unregister')
        
        assert response.status_code == 401


class TestGetMyEvents:
    """Test cases for getting user's events."""
    
    def test_get_my_events_success(self, client, authenticated_headers, sample_event):
        """Test getting user's registered events."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        # Register for event
        client.post(f'/events/{event_id}/register', headers=authenticated_headers)
        
        # Get user's events
        response = client.get('/me/events', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'events' in data
        assert len(data['events']) == 1
        
        event = data['events'][0]
        assert event['title'] == 'Test Event'
        assert event['description'] == 'This is a test event'
        assert event['channel'] == 'Hostages Square'
        assert event['language'] == 'Hebrew'
        assert event['location'] == 'Jerusalem'
        assert event['registration_status'] == 'approved'
    
    def test_get_my_events_empty(self, client, authenticated_headers):
        """Test getting user's events when no registrations."""
        response = client.get('/me/events', headers=authenticated_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'events' in data
        assert len(data['events']) == 0
    
    def test_get_my_events_unauthorized(self, client):
        """Test getting user's events without authentication."""
        response = client.get('/me/events')
        
        assert response.status_code == 401