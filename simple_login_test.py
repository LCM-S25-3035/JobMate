#!/usr/bin/env python3

from flask import Flask, request, jsonify
from app import create_app, db
from app.models.user import User

# Create a simple test Flask app
test_app = Flask(__name__)

@test_app.route('/')
def index():
    return '''
    <html>
    <body>
        <h1>Simple Login Test</h1>
        <form method="POST" action="/login">
            <p>Email: <input type="email" name="email" value="applicant@demo.com"></p>
            <p>Password: <input type="password" name="password" value="password123"></p>
            <p><input type="submit" value="Test Login"></p>
        </form>
    </body>
    </html>
    '''

@test_app.route('/login', methods=['POST'])
def test_login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Create the main app context to access the database
    main_app = create_app()
    with main_app.app_context():
        try:
            user = User.query.filter_by(email=email).first()
            if user:
                # Check password
                if user.check_password(password):
                    return f'''
                    <html>
                    <body>
                        <h1>✅ LOGIN SUCCESS!</h1>
                        <p>User ID: {user.id}</p>
                        <p>Email: {user.email}</p>
                        <p>Name: {user.first_name} {user.last_name}</p>
                        <p>User Type: {user.user_type}</p>
                        <p>Is Verified: {user.is_verified}</p>
                        <p><a href="/">Back to login</a></p>
                    </body>
                    </html>
                    '''
                else:
                    return '<h1>❌ Wrong password</h1><p><a href="/">Back</a></p>'
            else:
                return '<h1>❌ User not found</h1><p><a href="/">Back</a></p>'
        except Exception as e:
            return f'<h1>❌ Error: {str(e)}</h1><p><a href="/">Back</a></p>'

if __name__ == '__main__':
    test_app.run(debug=True, port=5003)
