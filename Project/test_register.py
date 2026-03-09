from app import create_app, db
from models import User

app = create_app()

with app.test_client() as client:
    print("Attempting registration...")
    response = client.post('/', data={
        'register': 'true',
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    print(f"Response Status: {response.status_code}")
    
    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        if user:
            print(f"SUCCESS: User created! ID: {user.id}")
            # Clean up
            db.session.delete(user)
            db.session.commit()
            print("User deleted after test.")
        else:
            print("FAILURE: User not found in database.")
