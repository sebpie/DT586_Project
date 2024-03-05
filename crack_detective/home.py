from flask import Blueprint, Flask, render_template, request, jsonify
import sqlite3
import os
import shutil

UPLOAD_DIR = "uploads"

bp = Blueprint('home', __name__)

# Route for the home page
@bp.route('/')
def home():
    username = request.args.get('username')
    return render_template('home.html', username=username)

@bp.route('/settings')
def settings():
    username = request.args.get('username')  # Retrieve the logged-in username
    return render_template('settings.html', username=username)  # Pass the username to the settings.html template

@bp.route('/gallery')
def gallery():
    return render_template('gallery.html')



def init_home(app: Flask):

    # ensure the instance folder exists
    try:
        os.makedirs(os.path.join(app.instance_path, UPLOAD_DIR))
    except OSError:
        pass


    @app.route('/create_folder', methods=['POST'])
    def create_folder():
        try:
            # Get folder name from the request JSON data
            data = request.json
            folder_name = data.get('folder_name')

            if folder_name:
                # Define the full path to the uploads directory
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

    @app.route('/list_folders', methods=['GET'])
    def list_folders():
        try:
            folder_path = os.path.join(app.instance_path, UPLOAD_DIR)  # Path to the folder where you store images
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

                uploads_dir = os.path.join(app.root_path, UPLOAD_DIR)
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

    @app.route('/users', methods=['GET'])
    def list_users():
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        connection.close()

        user_list = [{'id': user[0], 'username': user[1], 'password': user[2]} for user in users]

        return jsonify({'users': user_list})
