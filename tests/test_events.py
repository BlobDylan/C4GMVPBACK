import pytest
import json
from app import db
from app.models import User, Event, Registration
from datetime import datetime


class TestGetEvents:
    """Test cases for getting all events."""
    
    def test_get_events_success(self, client, sample_event):
        """Test getting all events successfully."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
        
        response = client.get('/events')
        
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
        assert event['status'] == 'pending'
        assert event['group_size'] == 10
        assert event['num_instructors_needed'] == 2
        assert event['num_representatives_needed'] == 1
        assert event['target_audience'] == 'Universities'
    
    def test_get_events_empty(self, client):
        """Test getting events when no events exist."""
        response = client.get('/events')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'events' in data
        assert len(data['events']) == 0
    
    def test_get_events_multiple(self, client):
        """Test getting multiple events."""
        with client.application.app_context():
            # Create multiple events
            event1 = Event(
                title="Event 1",
                description="First event",
                date=datetime(2024, 12, 31, 18, 0),
                channel="Hostages Square",
                language="Hebrew",
                location="Jerusalem",
                target_audience="Universities"
            )
            
            event2 = Event(
                title="Event 2",
                description="Second event",
                date=datetime(2025, 1, 15, 19, 0),
                channel="Virtual",
                language="English",
                location="Zoom",
                target_audience="Business Sector"
            )
            
            db.session.add(event1)
            db.session.add(event2)
            db.session.commit()
        
        response = client.get('/events')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'events' in data
        assert len(data['events']) == 2
        
        titles = [event['title'] for event in data['events']]
        assert 'Event 1' in titles
        assert 'Event 2' in titles


class TestGetEventRegistrants:
    """Test cases for getting event registrants."""
    
    def test_get_registrants_success(self, client, sample_event, sample_user):
        """Test getting registrants for an event."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.add(sample_event)
            db.session.commit()
            
            # Create registration
            registration = Registration(
                user_id=sample_user.id,
                event_id=sample_event.id,
                status="approved"
            )
            db.session.add(registration)
            db.session.commit()
            
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrants')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'registrants' in data
        assert len(data['registrants']) == 1
        
        registrant = data['registrants'][0]
        assert registrant['firstName'] == 'Test'
        assert registrant['lastName'] == 'User'
        assert registrant['email'] == 'test@example.com'
        assert registrant['role'] == 'Family Representative'
    
    def test_get_registrants_event_not_found(self, client):
        """Test getting registrants for non-existent event."""
        response = client.get('/events/999/registrants')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'Event not found'
    
    def test_get_registrants_no_registrants(self, client, sample_event):
        """Test getting registrants when no one is registered."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrants')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'registrants' in data
        assert len(data['registrants']) == 0
    
    def test_get_registrants_multiple_users(self, client, sample_event):
        """Test getting multiple registrants for an event."""
        with client.application.app_context():
            # Create multiple users
            user1 = User(
                first_name="User",
                last_name="One",
                email="user1@example.com",
                role="Family Representative"
            )
            user1.set_password("password123")
            
            user2 = User(
                first_name="User",
                last_name="Two",
                email="user2@example.com",
                role="Guide"
            )
            user2.set_password("password123")
            
            db.session.add(user1)
            db.session.add(user2)
            db.session.add(sample_event)
            db.session.commit()
            
            # Create registrations
            registration1 = Registration(
                user_id=user1.id,
                event_id=sample_event.id,
                status="approved"
            )
            registration2 = Registration(
                user_id=user2.id,
                event_id=sample_event.id,
                status="pending"
            )
            
            db.session.add(registration1)
            db.session.add(registration2)
            db.session.commit()
            
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrants')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'registrants' in data
        assert len(data['registrants']) == 2
        
        emails = [registrant['email'] for registrant in data['registrants']]
        assert 'user1@example.com' in emails
        assert 'user2@example.com' in emails


class TestGetEventPendingRegistrations:
    """Test cases for getting pending registrations for a specific event."""
    
    def test_get_event_pending_registrations_success(self, client, admin_headers, sample_event):
        """Test getting pending registrations for an event as admin."""
        with client.application.app_context():
            # Create guide user (their registrations are pending)
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
            
            # Create pending registration
            registration = Registration(
                user_id=guide.id,
                event_id=sample_event.id,
                status="pending"
            )
            db.session.add(registration)
            db.session.commit()
            
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrations/pending', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'registrations' in data
        assert len(data['registrations']) == 1
        
        registration = data['registrations'][0]
        assert registration['user_email'] == 'guide@example.com'
        assert registration['user_role'] == 'Guide'
        assert registration['status'] == 'pending'
        assert registration['event_title'] == 'Test Event'
    
    def test_get_event_pending_registrations_unauthorized(self, client, authenticated_headers, sample_event):
        """Test getting pending registrations without admin privileges."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrations/pending', headers=authenticated_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert data['message'] == 'Admin access required'
    
    def test_get_event_pending_registrations_event_not_found(self, client, admin_headers):
        """Test getting pending registrations for non-existent event."""
        response = client.get('/events/999/registrations/pending', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'Event not found'
    
    def test_get_event_pending_registrations_no_auth(self, client, sample_event):
        """Test getting pending registrations without authentication."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrations/pending')
        
        assert response.status_code == 401
    
    def test_get_event_pending_registrations_no_pending(self, client, admin_headers, sample_event):
        """Test getting pending registrations when none exist."""
        with client.application.app_context():
            # Create family rep user (their registrations are auto-approved)
            family_rep = User(
                first_name="Family",
                last_name="Rep",
                email="familyrep@example.com",
                role="Family Representative"
            )
            family_rep.set_password("password123")
            
            db.session.add(family_rep)
            db.session.add(sample_event)
            db.session.commit()
            
            # Create approved registration
            registration = Registration(
                user_id=family_rep.id,
                event_id=sample_event.id,
                status="approved"
            )
            db.session.add(registration)
            db.session.commit()
            
            event_id = sample_event.id
        
        response = client.get(f'/events/{event_id}/registrations/pending', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'registrations' in data
        assert len(data['registrations']) == 0