#!/usr/bin/env python3

from flask import Flask
import os

# Create a minimal Flask app with different configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def test():
    return '''
    <html>
    <body>
        <h1>✅ Minimal Flask Test Works!</h1>
        <p>If you can see this, Flask is working.</p>
        <form method="POST" action="/check">
            <input type="submit" value="Test Form Submit">
        </form>
    </body>
    </html>
    '''

@app.route('/check', methods=['POST'])
def check():
    return '<h1>✅ Form submission works!</h1><p><a href="/">Back</a></p>'

if __name__ == '__main__':
    print("Starting minimal Flask test on port 5004...")
    app.run(debug=False, port=5004, threaded=False, processes=1)
