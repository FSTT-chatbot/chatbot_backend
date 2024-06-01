from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Adnane@the@man@the@goat'

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.chatbotdb
users_collection = db.users

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        # Remove "Bearer " prefix from token if present
        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = users_collection.find_one({'username': data['username']})
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/')
def hi():
    return jsonify({'message': 'HELLO MAN!'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    users_collection.insert_one({'username': data['username'], 'password': hashed_password})
    return jsonify({'message': 'Registered successfully!'}), 201



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = users_collection.find_one({'username': data['username']})

    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Could not verify'}), 401

    token = jwt.encode({'username': user['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=240)}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token}), 200


@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': f'Hello, {current_user["username"]}! This is a protected route.'})

if __name__ == '__main__':
    app.run(debug=True)
