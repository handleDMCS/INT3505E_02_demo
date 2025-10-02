from flask import Flask
from flask_restx import Api, Resource, fields
import sqlite3

app = Flask(__name__)
api = Api(app, version='1.0', title='Library API',
    description='A simple Library Management API for book CRUD operations',
    doc='/docs'
)

ns = api.namespace('books', description='Book operations')

# Define API models for documentation
book_model = api.model('Book', {
    'id': fields.Integer(readonly=True, description='Book ID'),
    'name': fields.String(required=True, description='Book name'),
    'status': fields.String(required=True, description='Book status (available/borrowed)')
})

book_input = api.model('BookInput', {
    'name': fields.String(required=True, description='Book name'),
    'status': fields.String(required=True, description='Book status (available/borrowed)')
})

status_update = api.model('StatusUpdate', {
    'status': fields.String(required=True, description='New status (available/borrowed)')
})

def get_db():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

@ns.route('/')
class BookList(Resource):
    @ns.doc('list_books')
    @ns.marshal_list_with(book_model)
    def get(self):
        '''List all books'''
        conn = get_db()
        cursor = conn.execute('SELECT id, name, status FROM books')
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return books

    @ns.doc('create_book')
    @ns.expect(book_input)
    @ns.marshal_with(book_model, code=201)
    def post(self):
        '''Create a new book'''
        data = api.payload
        conn = get_db()
        cursor = conn.execute(
            'INSERT INTO books (name, status) VALUES (?, ?)',
            (data['name'], data['status'])
        )
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return {'id': book_id, 'name': data['name'], 'status': data['status']}, 201

@ns.route('/<int:id>')
@ns.response(404, 'Book not found')
@ns.param('id', 'The book identifier')
class Book(Resource):
    @ns.doc('get_book')
    @ns.marshal_with(book_model)
    def get(self, id):
        '''Get a book by ID'''
        conn = get_db()
        cursor = conn.execute('SELECT id, name, status FROM books WHERE id = ?', (id,))
        book = cursor.fetchone()
        conn.close()
        if book is None:
            api.abort(404, f"Book {id} not found")
        return dict(book)

    @ns.doc('update_book')
    @ns.expect(book_input)
    @ns.marshal_with(book_model)
    def put(self, id):
        '''Update a book'''
        data = api.payload
        conn = get_db()
        conn.execute(
            'UPDATE books SET name = ?, status = ? WHERE id = ?',
            (data['name'], data['status'], id)
        )
        conn.commit()
        conn.close()
        return {'id': id, 'name': data['name'], 'status': data['status']}

    @ns.doc('delete_book')
    @ns.response(204, 'Book deleted')
    def delete(self, id):
        '''Delete a book'''
        conn = get_db()
        conn.execute('DELETE FROM books WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return '', 204

@ns.route('/<int:id>/status')
@ns.param('id', 'The book identifier')
class BookStatus(Resource):
    @ns.doc('update_book_status')
    @ns.expect(status_update)
    @ns.marshal_with(book_model)
    def patch(self, id):
        '''Update book status (available/borrowed)'''
        data = api.payload
        status = data['status']
        
        if status not in ['available', 'borrowed']:
            api.abort(400, "Status must be 'available' or 'borrowed'")
        
        conn = get_db()
        cursor = conn.execute('SELECT id, name, status FROM books WHERE id = ?', (id,))
        book = cursor.fetchone()
        
        if book is None:
            conn.close()
            api.abort(404, f"Book {id} not found")
        
        conn.execute('UPDATE books SET status = ? WHERE id = ?', (status, id))
        conn.commit()
        conn.close()
        
        return {'id': id, 'name': book['name'], 'status': status}

if __name__ == '__main__':
    app.run(debug=True)