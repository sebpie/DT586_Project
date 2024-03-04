from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os 
import base64
import uuid
import shutil 
from datetime import datetime


app = Flask(__name__)
print(app.instance_path)

# Function to create the users table
def create_users_table():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

create_users_table()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            # Redirect the user to the homepage after successful login
              return redirect(url_for('home', username=username))
            
        else:
            error_message = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error_message)
    else:
        return render_template('login.html')

# Route for the home page
@app.route('/home')
def home():
    username = request.args.get('username')
    return render_template('home.html', username=username)

@app.route('/save_image', methods=['POST'])
def save_image():
    try:
        data = request.json
        image_data = data.get('image_data')
        if image_data:
            # Decode the base64 image data
            image_binary = base64.b64decode(image_data.split(',')[1])
            # Save the image to the images folder
            folder_name = datetime.now().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
            folder_path = os.path.join('images', folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            unique_id = uuid.uuid4().hex  # Generate a unique identifier
            image_filename = os.path.join(folder_path, f'captured_image_{unique_id}.png')
            with open(image_filename, 'wb') as f:
                f.write(image_binary)
            return jsonify({'message': 'Image saved successfully', 'filename': f'captured_image_{unique_id}.png'})
        else:
            return jsonify({'error': 'No image data received'})
    except Exception as e:
        return jsonify({'error': 'Error saving image: ' + str(e)})



@app.route('/create_folder', methods=['POST'])
def create_folder():
    try:
        # Get folder name from the request JSON data
        data = request.json
        folder_name = data.get('folder_name')

        if folder_name:
            # Define the full path to the uploads directory
            uploads_dir = os.path.join(app.root_path, 'uploads')
            folder_path = os.path.join(uploads_dir, folder_name)

            # Create folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                return jsonify({'message': f'Folder {folder_name} created successfully'})
            else:
                return jsonify({'error': f'Folder {folder_name} already exists'})
        else:
            return jsonify({'error': 'No folder name received'})
    except Exception as e:
        return jsonify({'error': 'Error creating folder: ' + str(e)})


@app.route('/list_folders', methods=['GET'])
def list_folders():
    try:
        folder_path = 'uploads'  # Path to the folder where you store images
        folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        return jsonify({'folders': folders})
    except Exception as e:
        return jsonify({'error': 'Error listing folders: ' + str(e)})

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    try:
       
        data = request.json
        folder_name = data.get('folder_name')

        if folder_name:
            
            uploads_dir = os.path.join(app.root_path, 'uploads')
            folder_path = os.path.join(uploads_dir, folder_name)

           
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                return jsonify({'message': f'Folder {folder_name} deleted successfully'})
            else:
                return jsonify({'error': f'Folder {folder_name} does not exist'})
        else:
            return jsonify({'error': 'No folder name received'})
    except Exception as e:
        return jsonify({'error': 'Error deleting folder: ' + str(e)})

@app.route('/settings')
def settings():
    
    username = request.args.get('username')  # Retrieve the logged-in username
    return render_template('settings.html', username=username)  # Pass the username to the settings.html template



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        connection.commit()
        connection.close()

        return redirect(url_for('list_users'))
    else:
        return render_template('register.html')

@app.route('/users', methods=['GET'])
def list_users():
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    connection.close()

    user_list = [{'id': user[0], 'username': user[1], 'password': user[2]} for user in users]

    return jsonify({'users': user_list})



@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

if __name__ == '__main__':
    app.run(debug=True)
