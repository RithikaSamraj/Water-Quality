from app import create_app, db
from models import User

app = create_app()

with app.app_context():
    print("Checking users table...")
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}")
        
    print("\nEnsuring table existence...")
    # This will print error if table doesn't exist
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT * FROM user'))
        print("User table accessible.")
    except Exception as e:
        print(f"Error accessing user table: {e}")
