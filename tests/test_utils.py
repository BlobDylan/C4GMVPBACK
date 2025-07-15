import pytest
from app import db
from app.models import User, Event, Registration
from app.utils.autoapprove import should_autoapprove_event
from app.utils.decorators import admin_required, super_admin_required
from flask import Flask, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime


class TestAutoApproveFunction:
    """Test cases for the auto-approve utility function."""
    
    def test_should_autoapprove_event_nonexistent_event(self, app):
        """Test auto-approve with non-existent event."""
        with app.app_context():
            result = should_autoapprove_event(999)
            assert result is False
    
    def test_should_autoapprove_event_no_registrations(self, app, sample_event):
        """Test auto-approve with no registrations."""
        with app.app_context():
            db.session.add(sample_event)
            db.session.commit()
            
            result = should_autoapprove_event(sample_event.id)
            assert result is False
    
    def test_should_autoapprove_event_with_family_rep(self, app, sample_event):
        """Test auto-approve with family representative registration."""
        with app.app_context():
            # Create family representative user
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
            
            # Create registration
            registration = Registration(
                user_id=family_rep.id,
                event_id=sample_event.id,
                status="approved"
            )
            db.session.add(registration)
            db.session.commit()
            
            result = should_autoapprove_event(sample_event.id)
            assert result is True
    
    def test_should_autoapprove_event_with_sufficient_guides(self, app, sample_event):
        """Test auto-approve with sufficient number of guides."""
        with app.app_context():
            # Set event to need 2 instructors
            sample_event.num_instructors_needed = 2
            db.session.add(sample_event)
            db.session.commit()
            
            # Create 2 guide users
            guide1 = User(
                first_name="Guide",
                last_name="One",
                email="guide1@example.com",
                role="Guide"
            )
            guide1.set_password("password123")
            
            guide2 = User(
                first_name="Guide",
                last_name="Two",
                email="guide2@example.com",
                role="Guide"
            )
            guide2.set_password("password123")
            
            db.session.add(guide1)
            db.session.add(guide2)
            db.session.commit()
            
            # Create registrations
            registration1 = Registration(
                user_id=guide1.id,
                event_id=sample_event.id,
                status="approved"
            )
            registration2 = Registration(
                user_id=guide2.id,
                event_id=sample_event.id,
                status="approved"
            )
            
            db.session.add(registration1)
            db.session.add(registration2)
            db.session.commit()
            
            result = should_autoapprove_event(sample_event.id)
            assert result is True
    
    def test_should_autoapprove_event_insufficient_guides(self, app, sample_event):
        """Test auto-approve with insufficient number of guides."""
        with app.app_context():
            # Set event to need 3 instructors
            sample_event.num_instructors_needed = 3
            db.session.add(sample_event)
            db.session.commit()
            
            # Create only 1 guide user
            guide = User(
                first_name="Guide",
                last_name="User",
                email="guide@example.com",
                role="Guide"
            )
            guide.set_password("password123")
            
            db.session.add(guide)
            db.session.commit()
            
            # Create registration
            registration = Registration(
                user_id=guide.id,
                event_id=sample_event.id,
                status="approved"
            )
            db.session.add(registration)
            db.session.commit()
            
            result = should_autoapprove_event(sample_event.id)
            assert result is False
    
    def test_should_autoapprove_event_mixed_roles(self, app, sample_event):
        """Test auto-approve with mixed user roles."""
        with app.app_context():
            # Set event to need 2 instructors
            sample_event.num_instructors_needed = 2
            db.session.add(sample_event)
            db.session.commit()
            
            # Create 1 guide and 1 family rep
            guide = User(
                first_name="Guide",
                last_name="User",
                email="guide@example.com",
                role="Guide"
            )
            guide.set_password("password123")
            
            family_rep = User(
                first_name="Family",
                last_name="Rep",
                email="familyrep@example.com",
                role="Family Representative"
            )
            family_rep.set_password("password123")
            
            db.session.add(guide)
            db.session.add(family_rep)
            db.session.commit()
            
            # Create registrations
            registration1 = Registration(
                user_id=guide.id,
                event_id=sample_event.id,
                status="approved"
            )
            registration2 = Registration(
                user_id=family_rep.id,
                event_id=sample_event.id,
                status="approved"
            )
            
            db.session.add(registration1)
            db.session.add(registration2)
            db.session.commit()
            
            # Should auto-approve because of family representative
            result = should_autoapprove_event(sample_event.id)
            assert result is True


class TestDecorators:
    """Test cases for permission decorators."""
    
    def test_admin_required_decorator(self, app):
        """Test admin_required decorator functionality."""
        @admin_required
        def protected_route():
            return jsonify({"message": "Access granted"})
        
        with app.app_context():
            # Create admin user
            admin = User(
                first_name="Admin",
                last_name="User",
                email="admin@example.com",
                permission_type="admin"
            )
            admin.set_password("password123")
            db.session.add(admin)
            db.session.commit()
            
            # Create access token
            token = create_access_token(identity=str(admin.id))
            
            # Test with admin user (should succeed)
            with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
                result = protected_route()
                assert result is not None
    
    def test_super_admin_required_decorator(self, app):
        """Test super_admin_required decorator functionality."""
        @super_admin_required
        def protected_route():
            return jsonify({"message": "Access granted"})
        
        with app.app_context():
            # Create super admin user
            super_admin = User(
                first_name="Super",
                last_name="Admin",
                email="superadmin@example.com",
                permission_type="super_admin"
            )
            super_admin.set_password("password123")
            db.session.add(super_admin)
            db.session.commit()
            
            # Create access token
            token = create_access_token(identity=str(super_admin.id))
            
            # Test with super admin user (should succeed)
            with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
                result = protected_route()
                assert result is not None
    
    def test_admin_required_with_regular_user(self, app):
        """Test admin_required decorator with regular user (should fail)."""
        @admin_required
        def protected_route():
            return jsonify({"message": "Access granted"})
        
        with app.app_context():
            # Create regular user
            user = User(
                first_name="Regular",
                last_name="User",
                email="user@example.com",
                permission_type="user"
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            
            # Create access token
            token = create_access_token(identity=str(user.id))
            
            # Test with regular user (should fail)
            with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
                result = protected_route()
                # Should return 403 response
                assert result[1] == 403
    
    def test_super_admin_required_with_admin(self, app):
        """Test super_admin_required decorator with admin user (should fail)."""
        @super_admin_required
        def protected_route():
            return jsonify({"message": "Access granted"})
        
        with app.app_context():
            # Create admin user (not super admin)
            admin = User(
                first_name="Admin",
                last_name="User",
                email="admin@example.com",
                permission_type="admin"
            )
            admin.set_password("password123")
            db.session.add(admin)
            db.session.commit()
            
            # Create access token
            token = create_access_token(identity=str(admin.id))
            
            # Test with admin user (should fail for super admin route)
            with app.test_request_context(headers={'Authorization': f'Bearer {token}'}):
                result = protected_route()
                # Should return 403 response
                assert result[1] == 403