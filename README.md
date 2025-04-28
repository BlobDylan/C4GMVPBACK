# Flask Auth API

## Setup Instructions

1. **Clone the repository**
2. **Create a virtual environment**  
   `python -m venv venv && source venv/bin/activate` (Linux/macOS)  
   `venv\Scripts\activate` (Windows)

3. **Install dependencies**  
   `pip install -r requirements.txt`

4. **Create a `.env` file**
   JWT_SECRET_KEY=your-secret-key

5. **Run the server**  
   `python run.py`

## API Endpoints

- `POST /signup` – Register a new user
- `POST /login` – Login and get JWT
- `POST /logout` – Invalidate token
- `GET /me` – Get current user
- `GET /protected` – Test protected route
