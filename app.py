from flask import Flask, request, make_response
from flask_restx import Api, Resource, fields
import sqlite3
import jwt
import hashlib
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

api = Api(app, version='1.0', title='Library API',
    description='A simple Library Management API for book CRUD operations with JWT authentication',
    doc='/docs',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type in the *'Value'* input box: **'Bearer &lt;JWT&gt;'**, where JWT is the token"
        }
    }
)

ns = api.namespace('books', description='Book operations')
auth_ns = api.namespace('auth', description='Authentication operations')

# Define API models
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

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

token_model = api.model('Token', {
    'token': fields.String(description='JWT access token'),
    'role': fields.String(description='User role')
})

def get_db():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def token_required(admin_only=False):
    """Decorator to verify JWT token and check permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            
            # Get token from Authorization header
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                try:
                    token = auth_header.split(' ')[1]  # Bearer <token>
                except IndexError:
                    api.abort(401, 'Invalid token format. Use: Bearer <token>')
            
            if not token:
                api.abort(401, 'Token is missing')
            
            try:
                # Decode token
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user_role = data['role']
                current_user_id = data['user_id']
                
                # Check if admin permission is required
                if admin_only and current_user_role != 'admin':
                    api.abort(403, 'Admin permission required for this operation')
                
                # Pass user info to the route
                kwargs['current_user'] = {'id': current_user_id, 'role': current_user_role}
                
            except jwt.ExpiredSignatureError:
                api.abort(401, 'Token has expired')
            except jwt.InvalidTokenError:
                api.abort(401, 'Invalid token')
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc('login')
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(token_model)
    def post(self):
        '''Login and get JWT token'''
        data = api.payload
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            api.abort(400, 'Username and password are required')
        
        conn = get_db()
        cursor = conn.execute(
            'SELECT id, username, password, role FROM users WHERE username = ?',
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user or user['password'] != hash_password(password):
            api.abort(401, 'Invalid username or password')
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return {'token': token, 'role': user['role']}

@ns.route('/')
class BookList(Resource):
    @ns.doc('list_books', security='Bearer')
    @token_required()
    def get(self, current_user):
        '''List all books (requires authentication) - Cached for 5 minutes'''
        conn = get_db()
        cursor = conn.execute('SELECT id, name, status FROM books')
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Create response with cache headers
        response = make_response(books, 200)
        response.headers['Cache-Control'] = 'private, max-age=300'  # Cache for 5 minutes
        response.headers['Content-Type'] = 'application/json'
        
        return response

    @ns.doc('create_book', security='Bearer')
    @ns.expect(book_input)
    @ns.marshal_with(book_model, code=201)
    @token_required(admin_only=True)
    def post(self, current_user):
        '''Create a new book (admin only)'''
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
    @ns.doc('get_book', security='Bearer')
    @token_required()
    def get(self, id, current_user):
        '''Get a book by ID (requires authentication) - Cached for 5 minutes'''
        conn = get_db()
        cursor = conn.execute('SELECT id, name, status FROM books WHERE id = ?', (id,))
        book = cursor.fetchone()
        conn.close()
        
        if book is None:
            api.abort(404, f"Book {id} not found")
        
        # Create response with cache headers
        response = make_response(dict(book), 200)
        response.headers['Cache-Control'] = 'private, max-age=300'  # Cache for 5 minutes
        response.headers['Content-Type'] = 'application/json'
        
        return response

    @ns.doc('update_book', security='Bearer')
    @ns.expect(book_input)
    @ns.marshal_with(book_model)
    @token_required(admin_only=True)
    def put(self, id, current_user):
        '''Update a book (admin only)'''
        data = api.payload
        conn = get_db()
        conn.execute(
            'UPDATE books SET name = ?, status = ? WHERE id = ?',
            (data['name'], data['status'], id)
        )
        conn.commit()
        conn.close()
        return {'id': id, 'name': data['name'], 'status': data['status']}

    @ns.doc('delete_book', security='Bearer')
    @ns.response(204, 'Book deleted')
    @token_required(admin_only=True)
    def delete(self, id, current_user):
        '''Delete a book (admin only)'''
        conn = get_db()
        conn.execute('DELETE FROM books WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return '', 204

@ns.route('/<int:id>/status')
@ns.param('id', 'The book identifier')
class BookStatus(Resource):
    @ns.doc('update_book_status', security='Bearer')
    @ns.expect(status_update)
    @ns.marshal_with(book_model)
    @token_required(admin_only=True)
    def patch(self, id, current_user):
        '''Update book status (admin only)'''
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