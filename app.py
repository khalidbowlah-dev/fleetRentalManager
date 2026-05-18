import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# This secret key is required to keep user sessions secure!
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
    # Updated SQL: We grab the trucks AND the username of the person who owns it
    trucks = db.execute('''
        SELECT trucks.*, users.username
        FROM trucks
        JOIN users ON trucks.owner_id = users.id
    ''').fetchall()
    db.close()
    return render_template('index.html', trucks=trucks)


# ==========================================
# NEW USER AUTHENTICATION ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Scramble the password for security before saving
        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, hashed_password))
            db.commit()

            # Automatically log the user in after they register
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

        # Check if user exists AND the password matches the saved secure hash
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear() # Erase the user's login session
    return redirect(url_for('index'))


# ==========================================
# UPDATED ADD TRUCK ROUTE
# ==========================================

@app.route('/add_truck', methods=['GET', 'POST'])
def add_truck():
    # SECURITY: Kick the user back to the login page if they aren't signed in!
    if 'user_id' not in session:
        flash("You must be logged in to add a vehicle.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        model = request.form['model']
        daily_rate = request.form['daily_rate']

        # Save the new truck, dynamically linked to whoever is currently logged in
        db = get_db_connection()
        db.execute('INSERT INTO trucks (owner_id, model, daily_rate) VALUES (?, ?, ?)',
                   (session['user_id'], model, daily_rate))
        db.commit()
        db.close()

        return redirect(url_for('index'))

    return render_template('add_truck.html')


if __name__ == '__main__':
   # init_db()
    app.run(debug=True)
