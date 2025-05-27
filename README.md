# Flask Auth API

## Setup Instructions

1. **Clone the repository**
2. **Create a virtual environment**  
   `python -m venv venv && source venv/bin/activate` (Linux/macOS)  
   `venv\Scripts\activate` (Windows)

3. **Install dependencies**  
   `pip install -r requirements.txt`

4. **Create a `.env` file**
   JWT_SECRET_KEY=secret_key
   FLASK_APP=run.py
   FLASK_DEBUG=True
   DATABASE_URL=sqlite:///app.db
   SUPER_ADMIN_EMAIL=superadmin@example.com
   SUPER_ADMIN_PASSWORD=123456

5. **Run the server**  
   `python run.py`

## API Endpoints

### Authentication

- `POST /signup` – Register a new user
- `POST /login` – Login and get JWT
- `POST /logout` – Invalidate token
- `GET /me` – Get current user info

### User Events

- `GET /me/events` – Get events user is registered for
- `POST /events/<event_id>/register` – Register for an event
- `DELETE /events/<event_id>/unregister` – Unregister from an event

### Events

- `GET /events` – Get all events
- `GET /events/<event_id>/registrants` – Get registrants for an event

### Admin Routes

- `POST /admin/new` – Create a new event (Admin required)
- `PUT /admin/edit/<event_id>` – Update an event (Admin required)
- `DELETE /admin/delete/<event_id>` – Delete an event (Admin required)
- `PUT /admin/approve/<event_id>` – Approve an event (Admin required)
- `PUT /admin/unapprove/<event_id>` – Set event to pending (Admin required)
- `PUT /admin/set-permission/<user_id>` – Change user permissions (Super Admin required)

## Permission Levels

- `user` – Basic user permissions
- `admin` – Can manage events
- `super_admin` – Can manage user permissions
