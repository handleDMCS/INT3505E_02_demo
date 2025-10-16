import sqlite3
import hashlib

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_database():
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Drop tables if exist (for clean slate)
    cursor.execute('DROP TABLE IF EXISTS books')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Create books table
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # Create users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Insert sample books
    sample_books = [
        ('The Great Gatsby', 'available'),
        ('To Kill a Mockingbird', 'borrowed'),
        ('1984', 'available'),
        ('Pride and Prejudice', 'available'),
        ('The Catcher in the Rye', 'borrowed')
    ]
    
    cursor.executemany(
        'INSERT INTO books (name, status) VALUES (?, ?)',
        sample_books
    )
    
    # Insert sample users with hashed passwords
    sample_users = [
        ('admin', hash_password('admin123'), 'admin'),
        ('superadmin', hash_password('super123'), 'admin'),
        ('user1', hash_password('user123'), 'user'),
        ('user2', hash_password('user456'), 'user')
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
        sample_users
    )
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    
    cursor.execute('SELECT id, username, role FROM users')
    users = cursor.fetchall()
    
    print("Database generated successfully!")
    print(f"\nTotal books inserted: {len(books)}")
    print("\nSample books:")
    for book in books:
        print(f"  ID: {book[0]}, Name: {book[1]}, Status: {book[2]}")
    
    print(f"\nTotal users inserted: {len(users)}")
    print("\nSample users:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
    
    print("\n--- Login Credentials ---")
    print("Admins:")
    print("  Username: admin, Password: admin123")
    print("  Username: superadmin, Password: super123")
    print("Users:")
    print("  Username: user1, Password: user123")
    print("  Username: user2, Password: user456")
    
    conn.close()

if __name__ == '__main__':
    generate_database()