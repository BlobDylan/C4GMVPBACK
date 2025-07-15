import pytest
import json
from app import db
from app.models import User, Event, Registration
from datetime import datetime


class TestCreateEvent:
    """Test cases for creating events (admin route)."""
    
    def test_create_event_success(self, client, admin_headers):
        """Test successful event creation by admin."""
        event_data = {
            'title': 'New Test Event',
            'description': 'A new test event',
            'date': '2024-12-31T18:00:00',
            'channel': 'Hostages Square',
            'language': 'Hebrew',
            'location': 'Jerusalem',
            'target_audience': 'Universities',
            'group_size': 15,
            'num_instructors_needed': 3,
            'num_representatives_needed': 2,
            'group_description': 'University students',
            'additional_notes': 'Bring notebooks'
        }
        
        response = client.post('/admin/new', json=event_data, headers=admin_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Event created'
        assert 'event' in data
        assert data['event']['title'] == 'New Test Event'
        assert data['event']['status'] == 'pending'
        
        # Check event was created in database
        with client.application.app_context():
            event = Event.query.filter_by(title='New Test Event').first()
            assert event is not None
            assert event.group_size == 15
    
    def test_create_event_missing_fields(self, client, admin_headers):
        """Test event creation with missing required fields."""
        event_data = {
            'title': 'Incomplete Event',
            'description': 'Missing required fields'
        }
        
        response = client.post('/admin/new', json=event_data, headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Missing required fields'
    
    def test_create_event_invalid_channel(self, client, admin_headers):
        """Test event creation with invalid channel."""
        event_data = {
            'title': 'Test Event',
            'description': 'Test description',
            'date': '2024-12-31T18:00:00',
            'channel': 'Invalid Channel',
            'language': 'Hebrew',
            'location': 'Jerusalem',
            'target_audience': 'Universities',
            'group_size': 10,
            'num_instructors_needed': 2,
            'num_representatives_needed': 1
        }
        
        response = client.post('/admin/new', json=event_data, headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['message'] == 'Invalid channel option'
    
    def test_create_event_unauthorized(self, client, authenticated_headers):
        """Test event creation without admin privileges."""
        event_data = {
            'title': 'Test Event',
            'description': 'Test description',
            'date': '2024-12-31T18:00:00',
            'channel': 'Hostages Square',
            'language': 'Hebrew',
            'location': 'Jerusalem',
            'target_audience': 'Universities',
            'group_size': 10,
            'num_instructors_needed': 2,
            'num_representatives_needed': 1
        }
        
        response = client.post('/admin/new', json=event_data, headers=authenticated_headers)
        
        assert response.status_code == 403


class TestUpdateEvent:
    """Test cases for updating events."""
    
    def test_update_event_success(self, client, admin_headers, sample_event):
        """Test successful event update."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        update_data = {
            'title': 'Updated Event Title',
            'group_size': 20
        }
        
        response = client.put(f'/admin/edit/{event_id}', json=update_data, headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Event updated'
        
        # Check event was updated in database
        with client.application.app_context():
            event = Event.query.get(event_id)
            assert event.title == 'Updated Event Title'
            assert event.group_size == 20
    
    def test_update_nonexistent_event(self, client, admin_headers):
        """Test updating non-existent event."""
        update_data = {'title': 'Updated Title'}
        
        response = client.put('/admin/edit/999', json=update_data, headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'Event not found'
    
    def test_update_event_unauthorized(self, client, authenticated_headers, sample_event):
        """Test event update without admin privileges."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        update_data = {'title': 'Updated Title'}
        
        response = client.put(f'/admin/edit/{event_id}', json=update_data, headers=authenticated_headers)
        
        assert response.status_code == 403


class TestDeleteEvent:
    """Test cases for deleting events."""
    
    def test_delete_event_success(self, client, admin_headers, sample_event):
        """Test successful event deletion."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.delete(f'/admin/delete/{event_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Event and all registrations deleted successfully'
        
        # Check event was deleted from database
        with client.application.app_context():
            event = Event.query.get(event_id)
            assert event is None
    
    def test_delete_nonexistent_event(self, client, admin_headers):
        """Test deleting non-existent event."""
        response = client.delete('/admin/delete/999', headers=admin_headers)
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['message'] == 'Event not found'
    
    def test_delete_event_unauthorized(self, client, authenticated_headers, sample_event):
        """Test event deletion without admin privileges."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.delete(f'/admin/delete/{event_id}', headers=authenticated_headers)
        
        assert response.status_code == 403


class TestApproveEvent:
    """Test cases for approving events."""
    
    def test_approve_event_success(self, client, admin_headers, sample_event):
        """Test successful event approval."""
        with client.application.app_context():
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.put(f'/admin/approve/{event_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Event approved'
        
        # Check event status was updated
        with client.application.app_context():
            event = Event.query.get(event_id)
            assert event.status == 'approved'
    
    def test_unapprove_event_success(self, client, admin_headers, sample_event):
        """Test setting event to pending status."""
        with client.application.app_context():
            sample_event.status = 'approved'
            db.session.add(sample_event)
            db.session.commit()
            event_id = sample_event.id
        
        response = client.put(f'/admin/unapprove/{event_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Event status set to pending'
        
        # Check event status was updated
        with client.application.app_context():
            event = Event.query.get(event_id)
            assert event.status == 'pending'


class TestSetUserPermission:
    """Test cases for setting user permissions."""
    
    def test_set_user_permission_success(self, client, super_admin_headers, sample_user):
        """Test successful permission update by super admin."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.commit()
            user_id = sample_user.id
        
        permission_data = {'permission_type': 'admin'}
        
        response = client.put(f'/admin/set-permission/{user_id}', 
                            json=permission_data, headers=super_admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'permission updated to' in data['message']
        
        # Check permission was updated
        with client.application.app_context():
            user = User.query.get(user_id)
            assert user.permission_type == 'admin'
    
    def test_set_user_permission_invalid_permission(self, client, super_admin_headers, sample_user):
        """Test setting invalid permission type."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.commit()
            user_id = sample_user.id
        
        permission_data = {'permission_type': 'invalid_permission'}
        
        response = client.put(f'/admin/set-permission/{user_id}', 
                            json=permission_data, headers=super_admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid permission type' in data['message']
    
    def test_set_user_permission_unauthorized(self, client, admin_headers, sample_user):
        """Test setting permissions without super admin privileges."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.commit()
            user_id = sample_user.id
        
        permission_data = {'permission_type': 'admin'}
        
        response = client.put(f'/admin/set-permission/{user_id}', 
                            json=permission_data, headers=admin_headers)
        
        assert response.status_code == 403


class TestRegistrationManagement:
    """Test cases for managing registrations."""
    
    def test_get_pending_registrations(self, client, admin_headers, sample_user, sample_event):
        """Test getting pending registrations."""
        with client.application.app_context():
            sample_user.role = "Guide"  # Guide registrations are pending
            db.session.add(sample_user)
            db.session.add(sample_event)
            db.session.commit()
            
            # Create pending registration
            registration = Registration(
                user_id=sample_user.id,
                event_id=sample_event.id,
                status="pending"
            )
            db.session.add(registration)
            db.session.commit()
        
        response = client.get('/admin/pending-registrations', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'registrations' in data
        assert len(data['registrations']) == 1
        assert data['registrations'][0]['registration_status'] == 'pending'
    
    def test_approve_registration(self, client, admin_headers, sample_user, sample_event):
        """Test approving a registration."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.add(sample_event)
            db.session.commit()
            
            # Create pending registration
            registration = Registration(
                user_id=sample_user.id,
                event_id=sample_event.id,
                status="pending"
            )
            db.session.add(registration)
            db.session.commit()
            
            user_id = sample_user.id
            event_id = sample_event.id
        
        response = client.put(f'/admin/approve-registration/{event_id}/{user_id}', 
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Registration approved'
        
        # Check registration was approved
        with client.application.app_context():
            registration = Registration.query.filter_by(
                user_id=user_id,
                event_id=event_id
            ).first()
            assert registration.status == 'approved'
    
    def test_reject_registration(self, client, admin_headers, sample_user, sample_event):
        """Test rejecting a registration."""
        with client.application.app_context():
            db.session.add(sample_user)
            db.session.add(sample_event)
            db.session.commit()
            
            # Create pending registration
            registration = Registration(
                user_id=sample_user.id,
                event_id=sample_event.id,
                status="pending"
            )
            db.session.add(registration)
            db.session.commit()
            
            user_id = sample_user.id
            event_id = sample_event.id
        
        response = client.delete(f'/admin/reject-registration/{event_id}/{user_id}', 
                               headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Registration rejected'
        
        # Check registration was deleted
        with client.application.app_context():
            registration = Registration.query.filter_by(
                user_id=user_id,
                event_id=event_id
            ).first()
            assert registration is None