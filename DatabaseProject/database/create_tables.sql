-- ===============================================
-- DATABASE STRUCTURE: Online Bookstore
-- ===============================================

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;

-- -------------------------
-- USERS TABLE
-- -------------------------
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
);

-- -------------------------
-- BOOKS TABLE
-- -------------------------
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    image TEXT DEFAULT 'default.jpg',
    description TEXT
);

-- -------------------------
-- ORDERS TABLE
-- -------------------------
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total REAL NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- -------------------------
-- ORDER_ITEMS TABLE
-- -------------------------
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- -------------------------
-- DATA INSERTION
-- -------------------------
INSERT INTO users (name, email, password, is_admin)
VALUES 
('Admin', 'admin@bookstore.com', 'admin123', 1),
('John Doe', 'john@example.com', 'password', 0);

INSERT INTO books (title, author, price, stock, description)
VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 10.99, 15, 'A classic American novel.'),
('To Kill a Mockingbird', 'Harper Lee', 8.50, 10, 'Pulitzer-winning story of justice and morality.'),
('1984', 'George Orwell', 9.75, 12, 'A dystopian vision of totalitarian society.');
