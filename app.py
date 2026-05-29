from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_fleet_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# WELCOME & PUBLIC CATALOG ROUTES
# ==========================================

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/catalog')
def catalog():
    db = get_db_connection()
    today_str = datetime.now().strftime('%Y-%m-%d')

    trucks = db.execute('''
        SELECT
            t.id, t.model, t.daily_rate, u.username, t.is_maintenance,
            (SELECT MAX(end_date) FROM bookings WHERE truck_id = t.id AND end_date >= ?) AS return_date,
            CASE
                WHEN t.is_maintenance = 1 THEN 'Maintenance'
                WHEN EXISTS (SELECT 1 FROM bookings WHERE truck_id = t.id AND end_date >= ?) THEN 'Rented'
                ELSE 'Available'
            END AS status
        FROM trucks t
        JOIN users u ON t.owner_id = u.id
    ''', (today_str, today_str)).fetchall()

    is_owner = False
    if 'user_id' in session:
        if session.get('role') == 'owner':
            is_owner = True

    db.close()
    return render_template('catalog.html', trucks=trucks, is_owner=is_owner)

# ==========================================
# OWNER DASHBOARD ROUTE
# ==========================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_owner'))

    db = get_db_connection()
    today_str = datetime.now().strftime('%Y-%m-%d')

    trucks = db.execute('''
        SELECT
            t.id, t.model, t.daily_rate, u.username, t.is_maintenance,
            (SELECT MAX(end_date) FROM bookings WHERE truck_id = t.id AND end_date >= ?) AS return_date,
            CASE
                WHEN t.is_maintenance = 1 THEN 'Maintenance'
                WHEN EXISTS (SELECT 1 FROM bookings WHERE truck_id = t.id AND end_date >= ?) THEN 'Rented'
                ELSE 'Available'
            END AS status
        FROM trucks t
        JOIN users u ON t.owner_id = u.id
        WHERE t.owner_id = ?
    ''', (today_str, today_str, session['user_id'])).fetchall()

    owner_bookings = db.execute('''
        SELECT b.id, t.model, u.username AS renter_name, b.start_date, b.end_date, b.total_cost
        FROM bookings b
        JOIN trucks t ON b.truck_id = t.id
        JOIN users u ON b.renter_id = u.id
        WHERE t.owner_id = ?
        ORDER BY b.start_date DESC
    ''', (session['user_id'],)).fetchall()

    total_revenue = sum([b['total_cost'] for b in owner_bookings])

    stats = {'total': 0, 'available': 0, 'rented': 0, 'maintenance': 0, 'revenue': total_revenue}
    for truck in trucks:
        stats['total'] += 1
        if truck['status'] == 'Available': stats['available'] += 1
        elif truck['status'] == 'Rented': stats['rented'] += 1
        elif truck['status'] == 'Maintenance': stats['maintenance'] += 1

    db.close()
    return render_template('index.html', trucks=trucks, stats=stats, owner_bookings=owner_bookings)

# ==========================================
# USER AUTHENTICATION ROUTES (SPLIT)
# ==========================================

@app.route('/register_owner', methods=['GET', 'POST'])
def register_owner():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'owner'

        db = get_db_connection()
        user_exists = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user_exists:
            flash("Error: Username already taken!")
            db.close()
            return redirect(url_for('register_owner'))

        hashed_pw = generate_password_hash(password)
        db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_pw, role))
        db.commit()

        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        db.close()

        flash("Registration successful! Welcome to the Fleet Manager.")
        return redirect(url_for('dashboard'))

    return render_template('register_owner.html')

@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'customer'

        db = get_db_connection()
        user_exists = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user_exists:
            flash("Error: Username already taken!")
            db.close()
            return redirect(url_for('register_customer'))

        hashed_pw = generate_password_hash(password)
        db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_pw, role))
        db.commit()

        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        db.close()

        flash("Registration successful! Welcome to the Fleet Catalog.")
        return redirect(url_for('catalog'))

    return render_template('register_customer.html')

# --- SPLIT LOGIN ROUTES ---

@app.route('/login_owner', methods=['GET', 'POST'])
def login_owner():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            # STRICT SECURITY CHECK: Only allow true Owners!
            if user['role'] == 'owner':
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                db.close()
                return redirect(url_for('dashboard'))
            else:
                db.close()
                flash("Access Denied: This is a Customer account. Please register a new account to become an Owner.")
                return redirect(url_for('login_owner'))
        else:
            db.close()
            flash("Error: Invalid username or password.")
            return redirect(url_for('login_owner'))

    return render_template('login_owner.html')


@app.route('/login_customer', methods=['GET', 'POST'])
def login_customer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            # STRICT SECURITY CHECK: Only allow true Customers!
            if user['role'] == 'customer':
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                db.close()
                return redirect(url_for('catalog'))
            else:
                db.close()
                flash("Access Denied: This is an Owner account. Please use the Owner Login portal.")
                return redirect(url_for('login_customer'))
        else:
            db.close()
            flash("Error: Invalid username or password.")
            return redirect(url_for('login_customer'))

    return render_template('login_customer.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('welcome'))

# ==========================================
# VEHICLE MANAGEMENT ROUTE
# [US1] Fleet Inventory Route: Handles creating new vehicles

@app.route('/add_truck', methods=['GET', 'POST'])
def add_truck():
    if 'user_id' not in session:
        flash("Please log in to add a truck.")
        return redirect(url_for('login_owner'))

    if request.method == 'POST':
        model = request.form['model']
        daily_rate = float(request.form['daily_rate'])

        db = get_db_connection()
        db.execute('INSERT INTO trucks (model, daily_rate, owner_id) VALUES (?, ?, ?)',
                   (model, daily_rate, session['user_id']))
        db.commit()
        db.close()

        flash(f"Successfully added {model} to the fleet!")
        return redirect(url_for('dashboard'))

    return render_template('add_truck.html')

# ==========================================
# BOOKING ENGINE
# [US2] Prevent Overlapping Bookings: Checks database for date conflicts

@app.route('/book/<int:truck_id>', methods=['GET', 'POST'])
def book_truck(truck_id):
    if 'user_id' not in session:
        flash("Please log in to book a vehicle.")
        return redirect(url_for('login_customer'))

    # STRICT SECURITY CHECK: Block Owners from booking vehicles!
    if session.get('role') == 'owner':
        flash("Action Denied: Fleet Owners cannot book vehicles. Please log in as a Customer to make a reservation.")
        return redirect(url_for('catalog'))

    db = get_db_connection()
    truck = db.execute('SELECT * FROM trucks WHERE id = ?', (truck_id,)).fetchone()
    today_str = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        start_str = request.form['start_date']
        end_str = request.form['end_date']

        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')

        # --- NEW VALIDATION: BLOCK PAST DATES ---
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_date < today:
            flash("Error: You cannot book a start date in the past!")
            db.close()
            return redirect(url_for('book_truck', truck_id=truck_id))
        # ----------------------------------------

        days = (end_date - start_date).days

        if days <= 0:
            flash("End date must be at least 1 day after the start date!")
            db.close()
            return redirect(url_for('book_truck', truck_id=truck_id))

        conflict = db.execute('''
            SELECT 1 FROM bookings
            WHERE truck_id = ?
            AND NOT (? >= end_date OR ? <= start_date)
        ''', (truck_id, start_str, end_str)).fetchone()

        if conflict:
            flash("Error: This truck is already reserved during those specific dates!")
            db.close()
            return redirect(url_for('book_truck', truck_id=truck_id))
# [US3] Dynamic Cost Calculation: Multiplies daily rate by total days

        total_cost = days * truck['daily_rate']

        db.execute('INSERT INTO bookings (truck_id, renter_id, start_date, end_date, total_cost) VALUES (?, ?, ?, ?, ?)',
                   (truck_id, session['user_id'], start_str, end_str, total_cost))
        db.commit()
        db.close()

        flash(f"Success! Booked for {days} days. Total: ${total_cost:.2f}")
        return redirect(url_for('my_bookings'))

    db.close()
    return render_template('book.html', truck=truck, today_str=today_str)

# ==========================================
# USER RENTAL HISTORY PANEL
# [US5] Customer Rental History: Fetches active and past receipts

@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        flash("Please log in to view your booking history.")
        return redirect(url_for('login_customer'))

    db = get_db_connection()
    user_bookings = db.execute('''
        SELECT bookings.*, trucks.model, trucks.daily_rate
        FROM bookings
        JOIN trucks ON bookings.truck_id = trucks.id
        WHERE bookings.renter_id = ?
        ORDER BY bookings.start_date DESC
    ''', (session['user_id'],)).fetchall()

    is_owner = False
    if session.get('role') == 'owner':
        is_owner = True

    today_str = datetime.now().strftime('%Y-%m-%d')

    db.close()
    return render_template('my_bookings.html', bookings=user_bookings, is_owner=is_owner, today_str=today_str)

# ==========================================
# CRUD: UPDATE & DELETE ROUTES
# ==========================================

@app.route('/edit_truck/<int:truck_id>', methods=['GET', 'POST'])
def edit_truck(truck_id):
    if 'user_id' not in session:
        return redirect(url_for('login_owner'))

    db = get_db_connection()
    truck = db.execute('SELECT * FROM trucks WHERE id = ? AND owner_id = ?', (truck_id, session['user_id'])).fetchone()

    if not truck:
        flash("Error: You can only edit vehicles that you own.")
        db.close()
        return redirect(url_for('dashboard'))

    today_str = datetime.now().strftime('%Y-%m-%d')
    is_rented = db.execute('SELECT 1 FROM bookings WHERE truck_id = ? AND end_date >= ?', (truck_id, today_str)).fetchone()

    if is_rented:
        flash("Error: You cannot modify the rate of a vehicle while it is currently rented!")
        db.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        new_rate = request.form['daily_rate']
        db.execute('UPDATE trucks SET daily_rate = ? WHERE id = ?', (new_rate, truck_id))
        db.commit()
        db.close()
        flash("Success: Vehicle daily rate updated!")
        return redirect(url_for('dashboard'))

    db.close()
    return render_template('edit_truck.html', truck=truck)

@app.route('/delete_truck/<int:truck_id>', methods=['POST'])
def delete_truck(truck_id):
    if 'user_id' not in session:
        return redirect(url_for('login_owner'))

    db = get_db_connection()
    truck = db.execute('SELECT * FROM trucks WHERE id = ? AND owner_id = ?', (truck_id, session['user_id'])).fetchone()

    if not truck:
        db.close()
        return redirect(url_for('dashboard'))

    today_str = datetime.now().strftime('%Y-%m-%d')
    is_rented = db.execute('SELECT 1 FROM bookings WHERE truck_id = ? AND end_date >= ?', (truck_id, today_str)).fetchone()

    if is_rented:
        flash("Error: You cannot delete a vehicle while it is currently rented by a customer!")
        db.close()
        return redirect(url_for('dashboard'))

    db.execute('DELETE FROM trucks WHERE id = ? AND owner_id = ?', (truck_id, session['user_id']))
    db.execute('DELETE FROM bookings WHERE truck_id = ?', (truck_id,))
    db.commit()
    db.close()

    flash("Vehicle successfully removed from the fleet.")
    return redirect(url_for('dashboard'))

# [US4] Vehicle Maintenance State: Toggles a truck offline/online
@app.route('/toggle_maintenance/<int:truck_id>', methods=['POST'])
def toggle_maintenance(truck_id):
    if 'user_id' not in session:
        return redirect(url_for('login_owner'))

    db = get_db_connection()
    truck = db.execute('SELECT is_maintenance FROM trucks WHERE id = ? AND owner_id = ?', (truck_id, session['user_id'])).fetchone()

    if truck:
        new_status = 0 if truck['is_maintenance'] else 1
        db.execute('UPDATE trucks SET is_maintenance = ? WHERE id = ?', (new_status, truck_id))
        db.commit()
        status_msg = "offline for Maintenance" if new_status else "back online and Available"
        flash(f"Vehicle status updated: It is now {status_msg}.")

    db.close()
    return redirect(url_for('dashboard'))

# ==========================================
# AUTO-BUILD DATABASE FUNCTION
# ==========================================
def auto_setup_db():
    conn = sqlite3.connect('database.db')
    try:
        conn.execute('SELECT 1 FROM trucks')
    except sqlite3.OperationalError:
        print("Building fresh database tables...")
        with open('schema.sql') as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    auto_setup_db()
    app.run(debug=True)