from flask import Flask, render_template, request, flash
import json
import os
import subprocess
import threading
import time

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # For flash messages

CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'CapstoneAutomation2', 'config.json')
MAIN_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'CapstoneAutomation2', 'main.py')

def shutdown_flask():
    time.sleep(3)  # Give time for the message to show
    os._exit(0)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        job_title = request.form['keywords']
        location = request.form['location']

        # Build the config dictionary
        config_data = {
            "email": email,
            "password": password,
            "Job Title": job_title,
            "location": location
        }

        try:
            # Save to JSON file
            os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
            with open(CONFIG_FILE_PATH, 'w') as config_file:
                json.dump(config_data, config_file, indent=4)

            # Run main.py automatically
            subprocess.Popen(['python', MAIN_SCRIPT_PATH])
            flash('🚀 LinkedIn bot started (main.py is running)... This window will close automatically.', 'success')

            # Shutdown Flask after a short delay
            threading.Thread(target=shutdown_flask).start()
        except Exception as e:
            flash(f'❌ Error: {e}', 'danger')

        # Do NOT redirect, just render the template so the message is visible
        return render_template('form.html')

    return render_template('form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)