from flask import Flask, request, jsonify
import jwt
import datetime
from flask_cors import CORS
from functools import wraps
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'Adnane@the@man@the@goat'
app.config['TOKEN_EXPIRATION'] = datetime.timedelta(days=1)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.chatbotdb
users_collection = db.users
conversations_collection = db.conversations
messages_collection = db.messages


def get_auth_user(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        current_user = users_collection.find_one({'email': data['email']})
        return current_user
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        if token.startswith("Bearer "):
            token = token.split(" ")[1]

        current_user = get_auth_user(token)
        if not current_user:
            return jsonify({'message': 'Token is invalid or has expired!'}), 403

        return f(current_user, *args, **kwargs)

    return decorated


@app.route('/')
def hi():
    return jsonify({'message': 'HELLO MAN!'})


@app.route('/register', methods=['POST'])
def register():
    print("register called")
    data = request.get_json()
    # Verify password matches confirmation password
    if data['password'] != data['confirm_password']:
        return jsonify({'error': 'Passwords do not match'}), 400

    # Check if user already exists
    elif users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'User already exists!'}), 400
    elif users_collection.find_one({'username': data['username']}):
        return jsonify({'error': 'Username already exists!'}), 400
    else:
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
        users_collection.insert_one({'username': data['username'], 'email': data['email'], 'password': hashed_password})
        # Generate access token with expiration time
        access_token = jwt.encode(
            {'email': data['email'], 'exp': datetime.datetime.utcnow() + app.config['TOKEN_EXPIRATION']},
            app.config['SECRET_KEY'], algorithm="HS256")
        user_id, username = read_user(data['email'])
        print("about to return in register")
    return jsonify({'user': {'id': user_id, 'username': username}, 'token': access_token}), 201


def read_user(email):
    user = users_collection.find_one({"email": email})
    if user:
        user['_id'] = str(user['_id'])
    return user['_id'], user['username']


@app.route('/login', methods=['POST'])
def login():
    print("login called")
    data = request.get_json()
    user_email = users_collection.find_one({'email': data['email']})

    if not user_email or not check_password_hash(user_email['password'], data['password']):
        return jsonify({'message': 'Could not verify'}), 401

    # Generate access token with expiration time
    access_token = jwt.encode(
        {'email': user_email['email'], 'exp': datetime.datetime.utcnow() + app.config['TOKEN_EXPIRATION']},
        app.config['SECRET_KEY'], algorithm="HS256")

    user_id, username = read_user(user_email['email'])
    print("about to return in login")
    return jsonify({'user': {'id': user_id, 'username': username}, 'token': access_token}), 200


@app.route('/protected', methods=['GET'])
@token_required
def protected(current_user):
    return jsonify({'message': f'Hello, {current_user["username"]}! This is a protected route.'})


@app.route('/users', methods=['GET'])
@token_required
def users(current_user):
    return jsonify({'message': f'Welcome, {current_user["username"]}! This is the users route.'})

@app.route('/user', methods=['GET'])
@token_required
def user(current_user):
    return jsonify({'username':current_user["username"]})

@app.route('/createConversation', methods=['POST'])
@token_required
def create_conversation(current_user):
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    print("hi 1")
    # Feed the user message to the model and get the model response
    model_response = run_model(user_message)

    # Create a new conversation in the database
    conversation = conversations_collection.insert_one({
        'name': 'Conversation with ' + current_user['username'],
        'created_at': datetime.datetime.utcnow(),
        'user_id': current_user['_id']
    })

    conversation_id = conversation.inserted_id
   

    user_message_id = messages_collection.insert_one(
        {
            'sender': 'user',
            'content': user_message,
            'created_at': datetime.datetime.utcnow(),
            'conversation_id': ObjectId(conversation_id)
        }
    ).inserted_id
    stored_user_message = messages_collection.find_one({"_id": user_message_id})

    chatbot_message_id = messages_collection.insert_one(
        {
            'sender': 'chatbot',
            'content': model_response,
            'created_at': datetime.datetime.utcnow(),
            'conversation_id': ObjectId(conversation_id)
        }
    ).inserted_id
    stored_chatbot_message = messages_collection.find_one({"_id": chatbot_message_id})
    
    return jsonify({
        'conversation': {
            'id': str(conversation_id),
            'name': 'Conversation with ' + current_user['username'],
            'created_at': datetime.datetime.utcnow().isoformat(),
            'user_id': str(current_user['_id'])
        },
        'user_message':{'id':str(stored_user_message['_id']),'content':stored_user_message['content'], 'sender':'user'},
        'prompt_response':{'id':str(stored_chatbot_message['_id']),'content':stored_chatbot_message['content'], 'sender':'chatbot'},
        
    }), 201


@app.route('/sendMessage/<conversation_id>', methods=['POST'])
@token_required
def add_message(current_user, conversation_id):
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    # Verify conversation exists
    conversation = conversations_collection.find_one({'_id': ObjectId(conversation_id), 'user_id': current_user['_id']})
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    # Feed the user message to the model and get the model response
    model_response = run_model(user_message)

   

    user_message_id = messages_collection.insert_one(
        {
            'sender': 'user',
            'content': user_message,
            'created_at': datetime.datetime.utcnow(),
            'conversation_id': ObjectId(conversation_id)
        }
    ).inserted_id
    stored_user_message = messages_collection.find_one({"_id": user_message_id})

    chatbot_message_id = messages_collection.insert_one(
        {
            'sender': 'chatbot',
            'content': model_response,
            'created_at': datetime.datetime.utcnow(),
            'conversation_id': ObjectId(conversation_id)
        }
    ).inserted_id
    stored_chatbot_message = messages_collection.find_one({"_id": chatbot_message_id})


    return jsonify({
        'user_message':{'id':str(stored_user_message['_id']),'content':stored_user_message['content'], 'sender':'user'},
        'prompt_response':{'id':str(stored_chatbot_message['_id']),'content':stored_chatbot_message['content'], 'sender':'chatbot'},
    }), 201


@app.route('/conversations', methods=['GET'])
@token_required
def get_user_conversations(current_user):
    user_conversations = conversations_collection.find({'user_id': current_user['_id']})
    conversations_list = []

    for conv in user_conversations:
        conversations_list.append({
            'id': str(conv['_id']),
            'name': conv['name'],
            'created_at': conv['created_at'].isoformat()
        })

    return jsonify({'conversations': conversations_list}), 200


@app.route('/messages/<conversation_id>', methods=['GET'])
@token_required
def get_conversation_messages(current_user, conversation_id):
    # Verify conversation exists and belongs to the current user
    conversation = conversations_collection.find_one({'_id': ObjectId(conversation_id), 'user_id': current_user['_id']})
    if not conversation:
        return jsonify({'error': 'Conversation not found'}), 404

    messages = messages_collection.find({'conversation_id': ObjectId(conversation_id)})
    messages_list = []

    for msg in messages:
        messages_list.append({
            'id': str(msg['_id']),
            'sender': msg['sender'],
            'content': msg['content'],
            'created_at': msg['created_at'].isoformat()
        })

    return jsonify({'messages': messages_list}), 200

def run_model(user_message):
    print("run_model called with message:", user_message)
    output = "this is a response, hi"
    return output


if __name__ == '__main__':
    app.run(debug=True)
