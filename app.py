import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_here'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        print("Database initialized!")

@app.route('/')
def index():
      db = get_db_connection()
      # Get today's date in 'YYYY-MM-DD' text format
      today_str = datetime.now().strftime('%Y-%m-%d')

      # Advanced SQL: Automatically calculate live status based on today's date
      trucks = db.execute('''
          SELECT
              trucks.id,
              trucks.model,
              trucks.daily_rate,
              users.username,
              CASE
                  WHEN EXISTS (
                      SELECT 1 FROM bookings
                      WHERE bookings.truck_id = trucks.id
                      AND ? BETWEEN bookings.start_date AND bookings.end_date
                  ) THEN 'Rented'
                  ELSE 'Available'
              END AS status
          FROM trucks
          JOIN users ON trucks.owner_id = users.id
      ''', (today_str,)).fetchall()

      db.close()
      return render_template('index.html', trucks=trucks)

# ==========================================
# USER AUTHENTICATION ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, hashed_password))
            db.commit()
            user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash("That username is already taken!")
            return redirect(url_for('register'))
        finally:
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ==========================================
# VEHICLE MANAGEMENT ROUTES
# ==========================================

@app.route('/add_truck', methods=['GET', 'POST'])
def add_truck():
    if 'user_id' not in session:
        flash("You must be logged in to add a vehicle.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        model = request.form['model']
        daily_rate = request.form['daily_rate']

        db = get_db_connection()
        db.execute('INSERT INTO trucks (owner_id, model, daily_rate) VALUES (?, ?, ?)',
                   (session['user_id'], model, daily_rate))
        db.commit()
        db.close()
        return redirect(url_for('index'))
    return render_template('add_truck.html')


# ==========================================
# NEW BOOKING ENGINE TRANSACTION ROUTE
# ==========================================

@app.route('/book/<int:truck_id>', methods=['GET', 'POST'])
def book_truck(truck_id):
    if 'user_id' not in session:
        flash("You must log in to reserve a heavy-duty truck.")
        return redirect(url_for('login'))

    db = get_db_connection()
    truck = db.execute('SELECT * FROM trucks WHERE id = ?', (truck_id,)).fetchone()

    if request.method == 'POST':
        start_str = request.form['start_date']
        end_str = request.form['end_date']

        # Turn the input text strings back into Python date objects
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')

        # Business logic: Calculate total delta days
        days = (end_date - start_date).days

        if days <= 0:
            flash("End date must be at least 1 day after the start date!")
            db.close()
            return redirect(url_for('book_truck', truck_id=truck_id))

        total_cost = days * truck['daily_rate']

        # Save transaction data to the SQLite database ledger
        db.execute('''
            INSERT INTO bookings (truck_id, renter_id, start_date, end_date, total_cost)
            VALUES (?, ?, ?, ?, ?)
        ''', (truck_id, session['user_id'], start_str, end_str, total_cost))

        db.commit()
        db.close()

        flash(f"Success! Booked for {days} days. Total: ${total_cost:.2f}")
        return redirect(url_for('index'))

    db.close()
    return render_template('book.html', truck=truck)
    # ==========================================
    # USER RENTAL HISTORY PANEL
    # ==========================================

    @app.route('/my_bookings')
    def my_bookings():
        # SECURITY: Kick out users who aren't logged in
        if 'user_id' not in session:
            flash("Please log in to view your booking history.")
            return redirect(url_for('login'))

        db = get_db_connection()

        # Grab all bookings for this user, including the truck details
        user_bookings = db.execute('''
            SELECT bookings.*, trucks.model, trucks.daily_rate
            FROM bookings
            JOIN trucks ON bookings.truck_id = trucks.id
            WHERE bookings.renter_id = ?
            ORDER BY bookings.start_date DESC
        ''', (session['user_id'],)).fetchall()

        db.close()
        return render_template('my_bookings.html', bookings=user_bookings)


if __name__ == '__main__':
    # init_db()
    app.run(debug=True)