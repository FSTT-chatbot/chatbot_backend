from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask import Flask, request, jsonify
import pymongo

# MongoDB Setup (Replace placeholders with your actual credentials)
client = MongoClient('mongodb://localhost:27017/')  # Default connection string
db_name = 'chatbotdb'  # Replace with your desired database name
db = client[db_name]  # Connect to the specified database
collection_name = 'users'  # Replace with your desired collection name
users_collection = db[collection_name]  # Create or reference the collection

def create_user(username, password):
    """
    Creates a new user in the MongoDB collection.

    Args:
        username (str): The username for the new user.
        password (str): The password for the new user (hashed before storage).

    Returns:
        str: The ID of the newly created user (if successful), otherwise None.
    """

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    user = {
        "username": username,
        "password": hashed_password
    }
    try:
        result = users_collection.insert_one(user)
        return str(result.inserted_id)
    except pymongo.errors.PyMongoError as e:
        print(f"Error creating user: {e}")
        return None

def create_user2(username, password):
    """
    Creates a new user in the MongoDB collection.

    Args:
        username (str): The username for the new user.
        password (str): The password for the new user (hashed before storage).

    Returns:
        str: The ID of the newly created user (if successful), otherwise None.
    """

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    user = {
        "username": username,
        "password": hashed_password,
        "test":"well well"
    }
    try:
        result = users_collection.insert_one(user)
        return str(result.inserted_id)
    except pymongo.errors.PyMongoError as e:
        print(f"Error creating user: {e}")
        return None

def read_user(username):
    """
    Reads and returns user data from the MongoDB collection based on username.

    Args:
        username (str): The username to search for.

    Returns:
        dict (or None): A dictionary containing user data if found, or None if not.
    """

    user = users_collection.find_one({"username": username})
    if user:
        user['_id'] = str(user['_id'])  # Convert MongoDB object ID to string
    return user

def update_user(username, new_password):
    """
    Updates the password for an existing user in the MongoDB collection.

    Args:
        username (str): The username of the user to update.
        new_password (str): The new password for the user (hashed before storage).

    Returns:
        int: The number of documents modified (1 if successful, 0 otherwise).
    """

    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    result = users_collection.update_one(
        {"username": username},
        {"$set": {"password": hashed_password}}
    )
    return result.modified_count

def delete_user(username):
    """
    Deletes a user from the MongoDB collection based on username.

    Args:
        username (str): The username of the user to delete.

    Returns:
        int: The number of documents deleted (1 if successful, 0 otherwise).
    """

    result = users_collection.delete_one({"username": username})
    return result.deleted_count


def print_all_users():
    users = users_collection.find()
    print("All users in the database:")
    for user in users:
        user['_id'] = str(user['_id'])
        print(json.dumps(user, indent=2))


def main():
    print("Testing CRUD operations with MongoDB\n")

    # Create
    username = "hi"
    password = "testpassword"
    print(f"Creating user: {username}")
    user_id = create_user(username, password)
    print(f"User created with ID: {user_id}\n")
    username2 = "adnane"
    password2 = "testpassword"
    create_user2(username2, password2)
    # Print all users to verify creation
    print_all_users()

    # Read
    print(f"Reading user: {username}")
    user = read_user(username)
    print(f"User data: {json.dumps(user, indent=2)}\n")

    # Update
    new_password = "newtestpassword"
    print(f"Updating user: {username} with new password")
    update_count = update_user(username, new_password)
    print(f"Number of users updated: {update_count}\n")

    # Read again to verify update
    print(f"Reading user: {username} after update")
    user = read_user(username)
    print(f"User data: {json.dumps(user, indent=2)}\n")

    # Print all users to verify update
    print_all_users()

    # Commenting out delete functionality for now
    print(f"Deleting user: {username}")
    delete_count = delete_user(username)
    print(f"Number of users deleted: {delete_count}\n")

    # Read again to verify deletion
    print(f"Reading user: {username} after deletion")
    user = read_user(username)
    print(f"User data: {json.dumps(user, indent=2)}")

    # Print all users to verify deletion
    print_all_users()


if __name__ == '__main__':
    main()
