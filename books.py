from flask import Flask, request, jsonify, render_template
from reviews import *
import sqlite3
import requests

BOOK_SERVICE_URL = "http://localhost:5001/api/books"

#Create an instance of Flask
books_app = Flask(__name__)

"""get_books_db_connection: gets database connection"""
def get_books_db_connection():
    connection = sqlite3.connect('books.db')
    connection.row_factory = sqlite3.Row
    return connection

"""init_books_db: executes script on database"""
def init_books_db():
    connection = get_books_db_connection()
    with open('books.sql', 'r') as file:
        connection.executescript(file.read())
    connection.commit()
    connection.close()

"""get_books: returns list of books in JSON format"""
@books_app.route('/api/books', methods=['GET'])
def get_books():
    connection = get_books_db_connection()
    books = connection.execute('SELECT * from books').fetchall()
    connection.close()
    return jsonify([dict(book) for book in books])

"""get_book: gets book data in JSON format"""
@books_app.route("/api/books/<int:book_id>", methods=['GET'])
def get_book(book_id):
    connection = get_books_db_connection()
    book = connection.execute('SELECT * FROM books WHERE id = ?', (book_id, )).fetchone()
    connection.close()
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(dict(book))

"""add_book: adds book to book database"""
@books_app.route('/api/books', methods=['POST'])
def add_book():
    data = request.form
    if not data:
        return jsonify({"error": "No data loaded"})
    required_fields = ['title', 'author', 'year']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    conn = get_books_db_connection()
    cursor = conn.execute(
    'INSERT INTO books (title, author, year) VALUES (?, ?, ?)',
    (data['title'], data['author'], data['year'])
    )
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'id': book_id, 'message': 'Book added successfully'}), 201

"""verify_book_exists: returns if a book exists"""
def verify_book_exists(book_id):
    try:
        response = requests.get(f'{BOOK_SERVICE_URL}/{book_id}')
        return response.status_code == 200
    except request.RequestException:
        return False
    
"""put_book: adds book to database using PUT method"""
@books_app.route('/api/books/<int:book_id>', methods=['PUT'])
def put_book(book_id):
    return add_book(book_id)

"""delete_book: deletes book from book database using DELETE method"""
@books_app.route('/api/books/<int:book_id>', methods=["DELETE"])
def delete_book(book_id):
    connection = get_books_db_connection()
    if(not verify_book_exists(book_id)):
        return jsonify({'error': 'Book does not exist.'})
    connection.execute('DELETE FROM books WHERE id = ?', (book_id,))
    connection.commit()
    connection.close()
    return jsonify({'id': book_id, 'message': 'Book was deleted successfully.'})

"""update_book: updates book information"""
@books_app.route('/api/update/books/<int:book_id>/<string:title>/<string:author>/<int:year>')
def update_book(book_id, title, author, year):
    connection = get_books_db_connection()
    if(not verify_book_exists(book_id)):
        return jsonify({'error': 'Book does not exist.'})
    connection.execute('UPDATE books SET title = ?, author = ?, year = ? WHERE id = ?',
                       (title, author, year, book_id,))
    connection.commit()
    connection.close()
    return jsonify({'id': book_id, 'message': 'Book was updated successfully.'})

"""books: displays all books to user"""
@books_app.route("/books")
def books():
    connection = get_books_db_connection()
    books = connection.execute("SELECT * FROM books").fetchall()
    connection.close()
    return render_template('books.html', books = books)

"""book_details: displays book details to user"""
@books_app.route("/books/<int:book_id>")
def book_details(book_id):
    connection = get_books_db_connection()
    book = connection.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    connection.close()
    connection = get_reviews_db_connection()
    reviews = connection.execute("SELECT * FROM reviews WHERE book_id = ?", (book_id,)).fetchall()
    connection.close()
    return render_template('reviews.html', book=book, reviews=reviews)

#Initialize the database if we are being ran
if __name__ == '__main__':
    init_books_db()
    books_app.run(host='0.0.0.0', port=5001)