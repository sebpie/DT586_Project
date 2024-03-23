from flask import Flask, current_app,render_template,send_from_directory,redirect, url_for,request, jsonify, Blueprint
import sqlite3
import os
import shutil
import base64
import datetime
import re


UPLOAD_DIR = "uploads"



bp = Blueprint('home', __name__)

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


@bp.route('/', methods=['GET', 'POST'])
def login():
    hide_navbar = True
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            return redirect(url_for('home.home', username=username))
        else:
            error_message = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error_message, hide_navbar=hide_navbar,username=username)
    else:
        return render_template('login.html', username='')
    
@bp.route('/settings')
def settings():
    username = request.args.get('username') 
    return render_template('settings.html', username=username)  

    
@bp.route('/change_password_without_auth', methods=['POST'])
def change_password_without_auth():
    username = request.form.get('username')
    new_password = request.form.get('newPassword')

    # Update the password in the database
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (new_password, username))
    connection.commit()
    connection.close()
    
    return jsonify({'message': 'Password changed successfully'})


# Route for the home page
@bp.route('/home')
def home():
    username = request.args.get('username')
    return render_template('home.html', username=username)

@bp.route('/gallery')
def gallery():
     folder_path = os.path.join(current_app.instance_path, UPLOAD_DIR)
     folders_with_images = []

     for folder_name in os.listdir(folder_path):
        folder_images = []

        # Get the list of images in the current folder
        folder_images_path = os.path.join(folder_path, folder_name)
        for filename in os.listdir(folder_images_path):
            if filename.endswith(".jpg"):
                image_url = f"/{UPLOAD_DIR}/{folder_name}/{filename}"
                folder_images.append(image_url)

        folders_with_images.append({'folder_name': folder_name, 'images': folder_images})

     return render_template('gallery.html', folders_with_images=folders_with_images)


def init_home(app: Flask):

    try:
        os.makedirs(os.path.join(app.instance_path, UPLOAD_DIR))
    except OSError:
        pass
    app.config['UPLOAD_FOLDER'] = UPLOAD_DIR

    @app.route('/api/folders', methods=['POST'])
    def create_folder():
        try:
            data = request.json
            folder_name = data.get('folder_name')

            if folder_name:
                uploads_dir = os.path.join(app.instance_path, UPLOAD_DIR)
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
        
    @app.route('/register', methods=['GET', 'POST'])
    def register():
       
       if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('cfrmpassword')
        username_pattern = r"^[a-zA-Z0-9]+$"
        if not re.match(username_pattern, username):
            error_message = 'Username must contain only letters and digits.'
            return render_template('register.html', error=error_message)
        password_pattern = r"^[a-zA-Z0-9]+$"
        if not re.match(password_pattern, password):
            error_message = 'Password must contain only letters and digits.'
            return render_template('register.html', error=error_message)
        if password != confirm_password:
            error_message = 'Password and Confirm Password do not match.'
            return render_template('register.html', error=error_message)
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        connection.commit()
        connection.close()
        return redirect(url_for('login'))
       else:
           return render_template('register.html')



    @app.route('/api/folders', methods=['GET'])
    def list_folders():
        try:
            folder_path = os.path.join(app.instance_path, UPLOAD_DIR)
            folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
            return jsonify({'folders': folders})
        except Exception as e:
            return jsonify({'error': 'Error listing folders: ' + str(e)})

    @app.route('/api/folders/<folder_name>', methods=['DELETE'])
    def delete_folder(folder_name):
        try:
            folder_path = os.path.join(app.instance_path, UPLOAD_DIR, folder_name)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                return jsonify({'message': f'Folder {folder_name} deleted successfully'})
            else:
                return jsonify({'error': f'Folder {folder_name} does not exist'}), 404
        except Exception as e:
            return jsonify({'error': 'Error deleting folder: ' + str(e)}), 500

    @app.route('/api/take_picture', methods=['POST'])
    def api_output():
        if request.method == 'POST':
             data = request.json
             folder_name = data.get('folder_name')
             screenshot_data = data.get('screenshot_data')
             print(f"Folder Name: {folder_name}")
             image_data = base64.b64decode(screenshot_data.split(',')[1])
             timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
             filename = f"{timestamp}.jpg"
             image_path = os.path.join(app.instance_path, UPLOAD_DIR, folder_name, filename)
             print(image_path)
             with open(image_path, 'wb') as f:
                 f.write(image_data)
             print(f"Screenshot saved to: {image_path}")

             return jsonify({'message': 'Data received and image saved successfully'})
        else :
             return jsonify({'error': 'Method Not Allowed'}), 405


    @app.route('/api/folders/<folder_name>')
    def get_folder_images(folder_name):
     folder_path = os.path.join(app.instance_path, UPLOAD_DIR, folder_name)
     images= [f'/{UPLOAD_DIR}/{folder_name}/{filename}' for filename in os.listdir(folder_path) if filename.endswith('.jpg')]
     return jsonify({'images': images})
    
    @app.route('/api/folders/<folder_name>/<filename>')
    def get_image(folder_name, filename):
     folder_path = os.path.join(app.instance_path, UPLOAD_DIR, folder_name)
     image_path = os.path.join(folder_path, filename)
     print(image_path)
     if os.path.exists(image_path) and filename.endswith('.jpg'):
        return send_from_directory(folder_path, filename)
     else:
        return 'Image not found', 404





    @app.route('/api/users', methods=['GET'])
    def list_users():
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        connection.close()

        user_list = [{'id': user[0], 'username': user[1], 'password': user[2]} for user in users]

        return jsonify({'users': user_list})
    
    
