import sqlite3

def generate_database():
    # Connect to database (creates file if it doesn't exist)
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # Drop table if exists (for clean slate)
    cursor.execute('DROP TABLE IF EXISTS books')
    
    # Create books table
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    # Insert sample data
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
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    
    print("Database generated successfully!")
    print(f"\nTotal books inserted: {len(books)}")
    print("\nSample data:")
    for book in books:
        print(f"  ID: {book[0]}, Name: {book[1]}, Status: {book[2]}")
    
    conn.close()

if __name__ == '__main__':
    generate_database()