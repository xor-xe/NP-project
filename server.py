from flask import Flask, request, jsonify
import os
import ssl
from cryptography.fernet import Fernet
app = Flask(__name__)

fnt = Fernet(Fernet.generate_key()) #declare Fernet

# Dummy data to store documents
files = {}

# get all files
# addr -> 127.0.0.1:5000/list_files
@app.route('/list_files', methods=['GET'])
def get_files():
    list_files = []
    for path in os.listdir("./storage"):
        list_files.append(path)

    return jsonify({'files': list_files}), 400


# get file
# addr -> 127.0.0.1:5000/file/file1.txt
@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        file = open(f"./storage/{file_id}", 'r')
        content = file.read()
        decMessage = fnt.decrypt(content).decode()
        return jsonify({'file': decMessage})
    except FileNotFoundError:
        return jsonify({'error': 'file can not be found'}), 404

# create file
# addr -> 127.0.0.1:5000/make_file
# input example -> {"name": "file1", "text": "hello world", "extension":"txt"}
@app.route('/make_file', methods=['POST'])
def create_file():    
    try:
        data = request.get_json()
        file_name = data.get('name') # Name of File
        file_text = data.get('text') # Text of file
        file_ext = data.get('extension') # Extension
        files[file_name] = file_text


        if file_text and file_name:

            if os.path.exists(f'./storage/{file_name}.{file_ext}'):
                return jsonify({'error': 'file already exists'}), 403
            else:
                file = open(f'./storage/{file_name}.{file_ext}', 'w')
                enc_txt = fnt.encrypt(file_text.encode()) # Fernet Encrypt
                file.write(enc_txt)
                file.close()
                return jsonify({'message': 'Document created successfully'}), 201
        else:
            return jsonify({'warning': 'file contents are empty'}), 400
    except:
        return jsonify({'error': 'error has occured'}), 400

# update file
# addr -> 127.0.0.1:5000/file/file1.txt
# input example -> {"text": "hello 2"}
@app.route('/file/<file_id>', methods=['PUT'])
def update_file(file_id):
    try:
        data = request.get_json()
        up_content = data.get('text')

        if up_content:
            if(not os.path.exists(f"./storage/{file_id}")):
                return jsonify({'error': 'file can not be found'}), 404
            
            file = open(f"./storage/{file_id}", 'w')
            enc_txt = fnt.encrypt(up_content.encode())
            file.write(enc_txt)

            file.close()

            return jsonify({'message': 'file updated'})
        else:
            return jsonify({'warning': 'file contents are empty'}), 400
    except :
        return jsonify({'error': 'something went wrong'}), 400


# delete file
# addr -> 127.0.0.1:5000/file/file1
@app.route('/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        if os.path.exists(f"./storage/{file_id}"):
            os.remove(f"./storage/{file_id}")
            return jsonify({'message': 'file deleted successfully'})
        else:
            return jsonify({'error': 'file not found'}), 404
    except Exception as e:
        return jsonify({'error': 'error occured'}), 500

        


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))