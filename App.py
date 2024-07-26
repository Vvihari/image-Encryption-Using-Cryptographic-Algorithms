from flask import Flask, request, jsonify, send_from_directory
from cryptography.fernet import Fernet
from werkzeug.utils import secure_filename, safe_join
import os

app = Flask(__name__, static_url_path='', static_folder='.')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Generate a key for encryption/decryption
# In a real application, you should save this key securely and not regenerate it each time the server starts
key = Fernet.generate_key()
cipher_suite = Fernet(key)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Read image file
        with open(file_path, 'rb') as f:
            file_data = f.read()

        # Encrypt image
        encrypted_data = cipher_suite.encrypt(file_data)

        encrypted_file_path = os.path.join(UPLOAD_FOLDER, 'encrypted_' + filename)
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_data)

        return jsonify({'encrypted_file_path': encrypted_file_path})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    encrypted_file_path = data.get('encrypted_file_path')
    if not encrypted_file_path:
        return jsonify({'error': 'No encrypted file path provided'}), 400

    filename = os.path.basename(encrypted_file_path)
    safe_encrypted_file_path = safe_join(UPLOAD_FOLDER, filename)
    if not os.path.exists(safe_encrypted_file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read encrypted file
    with open(safe_encrypted_file_path, 'rb') as f:
        encrypted_data = f.read()

    # Decrypt image
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    decrypted_file_path = os.path.join(UPLOAD_FOLDER, 'decrypted_' + filename.replace('encrypted_', ''))
    with open(decrypted_file_path, 'wb') as f:
        f.write(decrypted_data)

    return jsonify({'decrypted_file_path': decrypted_file_path})

if __name__ == '__main__':
    app.run(debug=True)
