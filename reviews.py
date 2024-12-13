from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import requests

BOOK_SERVICE_URL = "http://localhost:5001/api/books"

#Create an instance of flask
reviews_app = Flask(__name__)

"""get_reviews_db_connection: gets the database connection"""
def get_reviews_db_connection():
    connection = sqlite3.connect('reviews.db')
    connection.row_factory = sqlite3.Row
    return connection

"""init_reviews_db: executes sqlite script on database"""
def init_reviews_db():
    connection = get_reviews_db_connection()
    with open('reviews.sql', 'r') as file:
        connection.executescript(file.read())
    connection.commit()
    connection.close()

"""verify_book_exists: returns if a book exists"""
def verify_book_exists(book_id):
    try:
        response = requests.get(f'{BOOK_SERVICE_URL}/{book_id}')
        return response.status_code == 200
    except request.RequestException:
        return False

"""get_reviews: returns all reviews for a book using JSON format"""
@reviews_app.route("/api/reviews/<int:book_id>", methods=['GET'])
def get_reviews(book_id):
    connection = get_reviews_db_connection()
    reviews = connection.execute("SELECT * FROM reviews WHERE book_id = ?", (book_id,)).fetchall()
    connection.close()
    return jsonify([dict(review) for review in reviews])

"""add_review: adds review for book"""
@reviews_app.route("/api/reviews", methods=['POST'])
def add_review():
    data = request.form
    if not data:
        return jsonify({"error": "No data loaded"})
    required_fields = ['book_id', 'rating', 'comment', 'reviewer']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    if not verify_book_exists(data['book_id']):
        return jsonify({'error': 'Book not found'}), 404
    connection = get_reviews_db_connection()
    cursor = connection.execute('INSERT INTO reviews (book_id, rating, comment, reviewer, date) VALUES (?, ?, ?, ?, ?)',
                                (
                                    data['book_id'],
                                    data['rating'],
                                    data['comment'],
                                    data['reviewer'],
                                    datetime.now().strftime("%Y-%m-%d")
                                ))
    review_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return jsonify({'id': review_id, 'message' : 'Review added successfully'}), 201

    
"""put_review: adds review to database using PUT method"""
@reviews_app.route('/api/reviews/<int:review_id>', methods=['PUT'])
def put_review(book_id):
    return add_review(book_id)

"""delete_review: deletes review from review database using DELETE method"""
@reviews_app.route('/api/reviews/<int:review_id>', methods=["DELETE"])
def delete_review(review_id):
    connection = get_reviews_db_connection()
    connection.execute('DELETE FROM reviews WHERE id = ?', (review_id,))
    connection.commit()
    connection.close()
    return jsonify({'id': review_id, 'message': 'Review was deleted successfully.'})

"""update_review: updates review information"""
@reviews_app.route('/api/update/books/<int:review_id>/<int:book_id>/<int:rating>/<string:comment>/<string:reviewer>/<string:date>')
def update_review(review_id, book_id, rating, comment, reviewer, date):
    connection = get_reviews_db_connection()
    if(not verify_book_exists(book_id)):
        return jsonify({'error': 'Book does not exist.'})
    connection.execute('UPDATE reviews SET book_id = ?, rating = ?, comment = ?, reviewer = ?, date = ? WHERE id = ?',
                       (book_id, rating, comment, reviewer, date, review_id))
    connection.commit()
    connection.close()
    return jsonify({'id': book_id, 'message': 'Review was updated successfully.'})


#Create this database if we are being ran
if __name__ == '__main__':
    init_reviews_db()
    reviews_app.run(host='0.0.0.0', port=5002)