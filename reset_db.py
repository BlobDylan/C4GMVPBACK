# reset_db.py

from app import create_app, db

app = create_app()

with app.app_context():
    print("⏳ Dropping all tables...")
    db.drop_all()
    print("✅ All tables dropped.")

    print("⏳ Creating all tables...")
    db.create_all()
    print("✅ All tables created.")

    print("🎉 Database reset completed successfully.")
