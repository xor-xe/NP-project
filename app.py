from flask import Flask, request, jsonify
import os
import redis
from cryptography.fernet import Fernet
app = Flask(__name__)

f_key_file = open('./fernet_key.txt', 'rb')
f_key = f_key_file.read()

fnt = Fernet(f_key) #declare Fernet
# rsa_publicKey, rsa_privateKey = rsa.newkeys(2048)

# Dummy data to store documents
files = {}

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# get all files
# addr -> 127.0.0.1:5001/list_files
@app.route('/list_files', methods=['GET'])
def get_files():
    list_files = []
    for path in os.listdir("./storage"):
        list_files.append(path)

    return jsonify({'files': list_files}), 400


# get file
# addr -> 127.0.0.1:5001/file/file1.txt
@app.route('/file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        file = open(f"./storage/{file_id}", 'rb')
        content = file.read()
        print("dec", content)
        decMessage = fnt.decrypt(content).decode() # Fernet dencrypt
        return jsonify({'file': decMessage})
    except FileNotFoundError:
        return jsonify({'error': 'file can not be found'}), 404

# create file
# addr -> 127.0.0.1:5001/make_file
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
                file = open(f'./storage/{file_name}.{file_ext}', 'wb')
                enc_txt = fnt.encrypt(file_text.encode()) # Fernet Encrypt
                print("enc",enc_txt)
                # encMessage = rsa.encrypt(file_text.encode(), rsa_publicKey)
                file.write(enc_txt)
                file.close()
                return jsonify({'message': 'Document created successfully'}), 201
        else:
            return jsonify({'warning': 'file contents are empty'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# update file
# addr -> 127.0.0.1:5001/file/file1.txt
# input example -> {"text": "hello 2"}
@app.route('/file/<file_id>', methods=['PUT'])
def update_file(file_id):
    try:
        data = request.get_json()
        up_content = data.get('text')

        if up_content:
            if(not os.path.exists(f"./storage/{file_id}")):
                return jsonify({'error': 'file can not be found'}), 404
            
            file = open(f"./storage/{file_id}", 'wb')
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
    app.run(debug=True, host='0.0.0.0', port=5001, ssl_context=('cert.pem', 'key.pem'))