from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from models.user_model import register_user

from models.book_model import get_all_books
from models.order_model import create_order, add_order_item
from utils.pdf_utils import generate_receipt_pdf
from utils.email_utils import send_receipt_email
from models.order_model import create_order, add_order_item, save_receipt_path
from models.book_model import get_all_books, add_book, update_book, delete_book
from flask import Response







# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production!

# Path to database
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'bookstore.db')


# -------------------- DATABASE CONNECTION --------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------- ROUTES --------------------

@app.route('/')
def home():
    return render_template('index.html')






@app.route('/catalog')
def catalog():
    category = request.args.get('category')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    in_stock = request.args.get('in_stock')
    sort = request.args.get('sort')

    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if min_price:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    if in_stock:
        query += " AND stock > 0"

    #  SORTING LOGIC
    if sort == 'price_asc':
        query += " ORDER BY price ASC"
    elif sort == 'price_desc':
        query += " ORDER BY price DESC"

    conn = get_db_connection()
    books = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'catalog.html',
        books=books,
        selected_category=category
    )










@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    conn = get_db_connection()
    results = conn.execute("""
        SELECT * FROM books 
        WHERE title LIKE ? OR author LIKE ?
    """, (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()

    return render_template('search_results.html', query=query, results=results)







@app.route('/book/<int:book_id>')
def book_details(book_id):
    conn = get_db_connection()

    # Get the selected book
    book = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()

    if not book:
        conn.close()
        return "Book not found", 404

    # Get related books (same series, different ID)
    related = conn.execute("""
        SELECT * FROM books 
        WHERE series = ? AND id != ?
    """, (book['series'], book_id)).fetchall()

    conn.close()

    return render_template("book_details.html", book=book, related=related)








@app.route('/admin/export/orders')
def export_orders_csv():
    if session.get('is_admin') != 1:
        return redirect(url_for('home'))

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, user_id, total, order_date
        FROM orders
        ORDER BY order_date DESC
    """).fetchall()
    conn.close()

    def generate():
        yield "Order ID,User ID,Total,Order Date\n"
        for r in rows:
            yield f"{r['id']},{r['user_id']},{r['total']},{r['order_date']}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"}
    )







@app.route('/admin/export/top-books')
def export_books_csv():
    if session.get('is_admin') != 1:
        return redirect(url_for('home'))

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT b.title, SUM(oi.quantity) AS sold
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        GROUP BY b.title
        ORDER BY sold DESC
    """).fetchall()
    conn.close()

    def generate():
        yield "Title,Units Sold\n"
        for r in rows:
            yield f"{r['title']},{r['sold']}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=top_books.csv"}
    )






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = user['is_admin']

            # ⭐ FIX: Assign proper role
            session['role'] = 'admin' if user['is_admin'] == 1 else 'user'

            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')

    # If GET → show page
    return render_template('login.html')









@app.route('/logout')
def logout():
    if 'user_id' not in session:
        return redirect(url_for('home'))  # silently ignore

    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))








@app.route('/admin')
def admin():
    if 'user_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for("login"))

    if session.get('role') != 'admin':
        flash("Admin access required!", "danger")
        return redirect(url_for("home"))

    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()

    return render_template('admin.html', books=books)








@app.route('/admin/analytics')
def admin_analytics():
    if 'user_id' not in session or session.get('is_admin') != 1:
        flash('Admin access required.', 'danger')
        return redirect(url_for('home'))

    conn = get_db_connection()

    # 1️⃣ Total revenue
    total_revenue = conn.execute(
        'SELECT IFNULL(SUM(total), 0) FROM orders'
    ).fetchone()[0]

    # 2️⃣ Total orders
    total_orders = conn.execute(
        'SELECT COUNT(*) FROM orders'
    ).fetchone()[0]

    # 3️⃣ Best-selling books
    top_books = conn.execute("""
        SELECT b.title, SUM(oi.quantity) as sold
        FROM order_items oi
        JOIN books b ON oi.book_id = b.id
        GROUP BY b.title
        ORDER BY sold DESC
        LIMIT 5
    """).fetchall()

    # 4️⃣ Orders per day
    orders_by_day = conn.execute("""
        SELECT DATE(order_date) as day, COUNT(*) as count
        FROM orders
        GROUP BY day
        ORDER BY day ASC
    """).fetchall()

    conn.close()

    return render_template(
        'admin_analytics.html',
        total_revenue=total_revenue,
        total_orders=total_orders,
        top_books=top_books,
        orders_by_day=orders_by_day
    )








@app.route('/add_book', methods=['POST'])

def add_book_route():
    title = request.form['title']
    author = request.form['author']
    price = request.form['price']
    stock = request.form['stock']
    description = request.form.get('description')
    series = request.form.get('series')
    category = request.form.get('category') or "General"



    # Handle uploaded file
    file = request.files.get('image')
    image_filename = "default.jpg"

    if file and file.filename:
        image_filename = file.filename
        upload_path = os.path.join('static/images', image_filename)
        file.save(upload_path)

    add_book(title, author, price, stock, image_filename, description, series, category)

    flash('Book added successfully!', 'success')
    return redirect(url_for('admin'))






@app.route('/delete_book/<int:book_id>')
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    flash('Book deleted successfully.', 'info')
    return redirect(url_for('admin'))






@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        series = request.form.get('series')
        description = request.form.get('description')

        image_file = request.files.get('image')

        if image_file and image_file.filename:
            image_filename = image_file.filename
            image_path = os.path.join('static/images', image_filename)
            image_file.save(image_path)

            cursor.execute("""
                UPDATE books
                SET title = ?,
                    author = ?,
                    price = ?,
                    stock = ?,
                    category = ?,
                    series = ?,
                    description = ?,
                    image = ?
                WHERE id = ?
            """, (
                title, author, price, stock,
                category, series, description,
                image_filename, book_id
            ))
        else:
            cursor.execute("""
                UPDATE books
                SET title = ?,
                    author = ?,
                    price = ?,
                    stock = ?,
                    category = ?,
                    series = ?,
                    description = ?
                WHERE id = ?
            """, (
                title, author, price, stock,
                category, series, description,
                book_id
            ))

        conn.commit()
        conn.close()
        return redirect(url_for('admin'))

    # ---- LOAD BOOK ----
    cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    conn.close()

    # Convert row → dict for template compatibility
    book = {
        'id': row[0],
        'title': row[1],
        'author': row[2],
        'price': row[3],
        'stock': row[4],
        'category': row[5],
        'series': row[6],
        'description': row[7],
        'image': row[8]
    }

    return render_template('edit_book.html', book=book)









@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        try:
            register_user(name, email, password)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error: Email already exists or invalid input.', 'danger')

    return render_template('register.html')










@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    # Ensure user is logged in
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))

    # Initialize cart in session if not present
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']
    book_id_str = str(book_id)

    # Add or increase quantity
    if book_id_str in cart:
        cart[book_id_str] += 1
    else:
        cart[book_id_str] = 1

    session['cart'] = cart
    flash('Book added to cart!', 'success')
    return redirect(url_for('catalog'))










@app.route('/cart')
def cart():
    if 'cart' not in session or not session['cart']:
        return render_template('cart.html', cart_books=[], total=0)

    cart = session['cart']
    book_ids = list(map(int, cart.keys()))
    placeholders = ','.join(['?'] * len(book_ids))

    conn = get_db_connection()
    query = f"SELECT * FROM books WHERE id IN ({placeholders})"
    books = conn.execute(query, book_ids).fetchall()
    conn.close()

    # Calculate total
    total = 0
    cart_books = []
    for book in books:
        quantity = cart[str(book['id'])]
        subtotal = book['price'] * quantity
        total += subtotal
        cart_books.append({
            'id': book['id'],
            'title': book['title'],
            'author': book['author'],
            'price': book['price'],
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render_template('cart.html', cart_books=cart_books, total=total)






@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to place an order.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_name = session.get('username')
    user_email = session.get('user_email')

    # Get cart items
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('catalog'))

    # Fetch book info from DB
    book_ids = list(map(int, cart.keys()))
    placeholders = ','.join(['?'] * len(book_ids))

    conn = get_db_connection()
    books = conn.execute(f"SELECT * FROM books WHERE id IN ({placeholders})", book_ids).fetchall()
    conn.close()

    # Calculate cart items and total
    cart_items = []
    total_amount = 0
    for book in books:
        quantity = cart[str(book['id'])]
        subtotal = book['price'] * quantity
        total_amount += subtotal
        cart_items.append({
            'book_id': book['id'],
            'title': book['title'],
            'author': book['author'],
            'price': book['price'],
            'quantity': quantity,
            'subtotal': subtotal
        })

    # Handle POST → place order
    if request.method == 'POST':
        address = request.form.get('address')
        phone = request.form.get('phone')
        receipt_email = request.form.get('receipt_email')

        # -------- SIMULATED PAYMENT --------
        card_number = request.form.get('card_number', '').strip()
        card_exp = request.form.get('card_exp', '').strip()
        card_cvv = request.form.get('card_cvv', '').strip()

        errors = []

        # Basic validations (demo only)
        raw_digits = ''.join(ch for ch in card_number if ch.isdigit())
        if len(raw_digits) < 13 or len(raw_digits) > 19:
            errors.append('Invalid card number (simulation check).')
        if not card_exp or len(card_exp) < 3:
            errors.append('Invalid expiration date (simulation check).')
        if not card_cvv or not card_cvv.isdigit() or len(card_cvv) not in (3, 4):
            errors.append('Invalid CVV (simulation check).')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('checkout.html',
                                   cart_items=cart_items,
                                   total_amount=total_amount,
                                   user_name=user_name,
                                   user_email=user_email)

        # MASK card before any further usage
        masked_card = "**** **** **** " + raw_digits[-4:]

        # Create a TEMP table (simulation only)
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("CREATE TEMP TABLE temp_payment (card_mask TEXT, card_exp TEXT, ok INTEGER);")
            cur.execute("INSERT INTO temp_payment (card_mask, card_exp, ok) VALUES (?, ?, 1)",
                        (masked_card, card_exp))
            test_row = cur.execute("SELECT card_mask FROM temp_payment LIMIT 1").fetchone()
            if not test_row:
                raise Exception("Temporary payment table error.")

            cur.execute("DROP TABLE temp_payment;")
            conn.commit()

        except Exception as e:
            try:
                cur.execute("DROP TABLE IF EXISTS temp_payment;")
                conn.commit()
            except:
                pass
            flash("Payment simulation failed. Try again.", "danger")
            conn.close()
            return render_template("checkout.html",
                                   cart_items=cart_items,
                                   total_amount=total_amount,
                                   user_name=user_name,
                                   user_email=user_email)

        conn.close()
        # -------- END OF SIMULATED PAYMENT --------

        # Create order
        order_id = create_order(user_id, total_amount, address, phone, receipt_email)

        # Add items to order
        for item in cart_items:
            add_order_item(order_id, item['book_id'], item['quantity'], item['price'])

        # Generate PDF receipt
        pdf_path = generate_receipt_pdf(order_id, user_name, cart_items, total_amount, masked_card)
        save_receipt_path(order_id, pdf_path)

        # Send receipt email if provided
        if receipt_email:
            send_receipt_email(receipt_email, pdf_path)
        # Clear cart
        session['cart'] = {}
        flash('Order placed successfully!', 'success')

        # 🔥 Show success page instead of refreshing checkout
        return render_template('success.html')

    # Handle GET → show checkout page
    return render_template('checkout.html',
                           cart_items=cart_items,
                           total_amount=total_amount,
                           user_name=user_name,
                           user_email=user_email)






@app.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        flash('Please log in to view your orders.', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC', (user_id,)).fetchall()

    # For each order, get its items
    order_data = []
    for order in orders:
        items = conn.execute('''
            SELECT books.title, books.author, order_items.quantity, order_items.price
            FROM order_items
            JOIN books ON order_items.book_id = books.id
            WHERE order_items.order_id = ?
        ''', (order['id'],)).fetchall()

        order_data.append({
            'id': order['id'],
            'date': order['order_date'],
            'total': order['total'],
            'items': items
        })

    conn.close()
    return render_template('my_orders.html', orders=order_data)








#UPDATE books SET series = 'ASOIAF' WHERE title LIKE '%Storm of Swords%';

#UPDATE books SET series = 'ASOIAF' WHERE title LIKE '%Feast for Crows%';

#UPDATE books SET series = 'ASOIAF' WHERE title LIKE '%Dance with Dragons%';

#UPDATE users SET is_admin = 1 WHERE id = 2;

#DELETE FROM users WHERE id = 2;








#SQL INJECTION EXAMPLE : 

#SELECT email, password
#FROM Users
#WHERE email = 'admin@bookstore.com'
#AND password = '' OR '1'='1';









#CREATE TABLE IF NOT EXISTS reviews (
#id INTEGER PRIMARY KEY AUTOINCREMENT,
# user_id INTEGER NOT NULL,
#   book_id INTEGER NOT NULL,
#    rating INTEGER,
#  #  comment TEXT
#);








#SELECT 
#    users.username,
#   books.title,
#    order_items.quantity,
#    orders.created_at
#FROM orders
#JOIN users ON orders.user_id = users.id
#JOIN order_items ON order_items.order_id = orders.id
#JOIN books ON order_items.book_id = books.id;




# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(debug=True)
