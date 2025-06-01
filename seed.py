import json
import requests

# === CONFIG ===
BASE_URL = "http://localhost:5000"  # Change if your server runs elsewhere
LOGIN_ENDPOINT = f"{BASE_URL}/login"
CREATE_EVENT_ENDPOINT = f"{BASE_URL}/admin/new"

SUPER_ADMIN_EMAIL = "superadmin@example.com"
SUPER_ADMIN_PASSWORD = "123456"
EVENTS_FILE = "example_events.json"


# === LOGIN ===
def get_access_token():
    response = requests.post(
        LOGIN_ENDPOINT,
        json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
    )
    if response.status_code != 200:
        raise Exception(f"Login failed: {response.json()}")

    return response.json()["access_token"]


# === SEED EVENTS ===
def seed_events(token):
    headers = {"Authorization": f"Bearer {token}"}

    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        events = json.load(f)

    for i, event in enumerate(events):
        print(f"Seeding event {i+1}/{len(events)}: {event['title']}")

        response = requests.post(CREATE_EVENT_ENDPOINT, json=event, headers=headers)
        if response.status_code == 201:
            print("  ✅ Created")
        else:
            print(f"  ❌ Failed: {response.status_code} - {response.text}")


# === MAIN ===
if __name__ == "__main__":
    try:
        token = get_access_token()
        seed_events(token)
    except Exception as e:
        print(f"Error: {e}")
