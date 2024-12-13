from flask import Flask, request, jsonify, render_template
import sqlite3

# Create an instance of Flask
users_app = Flask(__name__)

"""get_users_db_connection: gets the database connection"""
def get_users_db_connection():
    connection = sqlite3.connect('users.db')
    connection.row_factory = sqlite3.Row
    return connection

"""init_users_db: executes sqlite script on database"""
def init_users_db():
    connection = get_users_db_connection()
    with open('users.sql', 'r') as file:
        connection.executescript(file.read())
    connection.commit()
    connection.close()

"""add_user: adds a new user to the database"""
@users_app.route("/api/users", methods=['POST'])
def add_user():
    data = request.form  # Get data from JSON request
    if not data:
        return jsonify({"error": "No data provided"}), 400
    required_fields = ['username', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: username and email'}), 400
    connection = get_users_db_connection()
    cursor = connection.execute('INSERT INTO users (username, email, pass) VALUES (?, ?, ?)',
                                 (data['username'], data['email'], data['password']))
    user_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return jsonify({'id': user_id, 'message': 'User added successfully'}), 201

"""get_all_users: retrieves all users from the database"""
@users_app.route("/api/users", methods=['GET'])
def get_all_users():
    connection = get_users_db_connection()
    users = connection.execute("SELECT * FROM users").fetchall()
    connection.close()
    return jsonify([dict(user) for user in users])

"""users: index page of users service"""
@users_app.route("/users", methods=["GET"])
def users():
    connection = get_users_db_connection()
    users = connection.execute("SELECT * FROM users").fetchall()
    connection.close()
    return render_template('users.html', users=users)

# Create this database if we are being ran
if __name__ == '__main__':
    init_users_db()
    users_app.run(host='0.0.0.0', port=5000)