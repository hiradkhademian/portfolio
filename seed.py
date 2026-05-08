# seed.py
from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if test user already exists
    if not User.query.filter_by(email="test@example.com").first():
        test_user = User(
            full_name="Test User", 
            email="test@example.com", 
            phone="123456789",
            password=generate_password_hash("test1234")
        )
        db.session.add(test_user)
        db.session.commit()
        print("Database seeded with a test user: test@example.com")
    else:
        print("Test user already exists in the database.")