from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os, sqlite3, uuid
from werkzeug.utils import secure_filename

# ------------------ Flask Setup ------------------
app = Flask(__name__)
app.secret_key = 'super-secret-key-change-this'  # Needed for session/cart

# Static upload folder (absolute path)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------ Database Helper ------------------
DB_FILE = os.path.join(BASE_DIR, "bakery.db")  # unified DB name

def db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db():
    """Create DB & table if they don't exist."""
    with db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                image TEXT,
                price REAL DEFAULT 0
            )
            """
        )
        conn.commit()

ensure_db()

# ------------------ Template Globals ------------------
@app.context_processor
def inject_globals():
    cart = session.get('cart', {})
    count = sum(int(q) for q in cart.values()) if isinstance(cart, dict) else 0
    return {
        "brand": "Leen’s Treats",
        "cart_count": count
    }

# ------------------ Helpers ------------------
def _get_cart():
    """Initialize cart in session if not present"""
    if 'cart' not in session or not isinstance(session['cart'], dict):
        session['cart'] = {}  # { product_id: qty }
    return session['cart']

def _cart_items_with_totals():
    """Return list of items in cart with product details and a grand total."""
    cart = _get_cart()
    if not cart:
        return [], 0.0

    ids = [k for k in cart.keys() if str(k).isdigit()]
    if not ids:
        return [], 0.0

    placeholders = ",".join(["?"] * len(ids))
    with db_connection() as conn:
        rows = conn.execute(f"SELECT * FROM cakes WHERE id IN ({placeholders})", ids).fetchall()

    items, grand_total = [], 0.0
    for row in rows:
        pid = str(row['id'])
        qty = max(0, int(cart.get(pid, 0)))
        price = float(row['price'] or 0)
        subtotal = qty * price
        grand_total += subtotal
        items.append({
            "id": row["id"],
            "name": row["name"],
            "image": row["image"],
            "price": price,
            "qty": qty,
            "subtotal": subtotal
        })
    return items, round(grand_total, 2)

def _allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ------------------ Routes ------------------
@app.route('/')
def index():
    with db_connection() as conn:
        cakes = conn.execute('SELECT * FROM cakes ORDER BY id DESC').fetchall()
    return render_template('index.html', cakes=cakes)

@app.route('/admin')
def admin():
    with db_connection() as conn:
        cakes = conn.execute('SELECT * FROM cakes ORDER BY id DESC').fetchall()
    return render_template('admin.html', cakes=cakes)

@app.route('/add', methods=['GET', 'POST'])
def add_cake():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip()
        try:
            price = float(request.form.get('price') or 0)
        except ValueError:
            price = 0.0

        if not name:
            flash('⚠️ Name is required.')
            return redirect(url_for('add_cake'))

        # Handle image upload safely
        image = request.files.get('image')
        filename = None
        if image and image.filename:
            if _allowed_file(image.filename):
                ext = os.path.splitext(secure_filename(image.filename))[1].lower()
                filename = f"{uuid.uuid4().hex}{ext}"
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('⚠️ Unsupported image type. Use png/jpg/jpeg/webp/gif.')
                return redirect(url_for('add_cake'))

        with db_connection() as conn:
            conn.execute(
                'INSERT INTO cakes (name, description, image, price) VALUES (?, ?, ?, ?)',
                (name, description, filename, price)
            )
            conn.commit()

        flash('🎂 New cake added!')
        return redirect(url_for('admin'))

    return render_template('add_cake.html')

# ------------------ Cart Endpoints ------------------
@app.route('/add_to_cart/<int:cake_id>', methods=['POST'])
def add_to_cart(cake_id):
    cart = session.get('cart', {})
    cart[str(cake_id)] = cart.get(str(cake_id), 0) + int(request.form.get('quantity', 1))
    session['cart'] = cart

    # Update cart count
    session['cart_count'] = sum(cart.values())

    flash("Item added to cart!")  # optional if you want Flask messages
    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    items, total = _cart_items_with_totals()
    return render_template('cart.html', items=items, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = _get_cart()
    for key, value in request.form.items():
        if key.startswith('qty_'):
            pid = key.split('_', 1)[1]
            try:
                qty = max(0, int(value or 0))
            except ValueError:
                qty = 0
            if qty == 0 and pid in cart:
                del cart[pid]
            else:
                cart[pid] = qty
    session.modified = True
    flash('🧮 Cart updated!')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:cake_id>', methods=['POST'])
def remove_from_cart(cake_id):
    cart = _get_cart()
    cart.pop(str(cake_id), None)
    session.modified = True
    flash('🗑️ Item removed.')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    items, total = _cart_items_with_totals()
    if request.method == 'POST':
        name = request.form.get("name")
        address = request.form.get("address")
        phone = request.form.get("phone")
        payment = request.form.get("payment")

        # Save order details into DB (optional future)
        # For now, just clear cart & show success page
        session.pop('cart', None)

        flash(f"✅ Thank you {name}! Your order has been placed successfully.")
        return redirect(url_for('order_success'))

    return render_template('checkout.html', items=items, total=total)

@app.route('/order_success')
def order_success():
    """Order success page with sparkles 🎉"""
    return render_template('order_success.html')

# ------------------ Extra Pages ------------------
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/menu")
def menu():
    with db_connection() as conn:
        cakes = conn.execute("SELECT * FROM cakes ORDER BY id DESC").fetchall()
    return render_template("menu.html", cakes=cakes)

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Favicon (avoid 404 during dev)
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ------------------ Run Server ------------------
if __name__ == '__main__':
    app.run(debug=True)
