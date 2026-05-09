import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' # Needed for sessions later

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# This function will create the database using your schema.sql
def init_db():
    with app.app_context():
        db = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        print("Database initialized!")

@app.route('/')
def index():
    return "<h1>Fleet Manager is Running!</h1><p>The database is ready.</p>"

@app.route('/add_truck', methods=['GET', 'POST'])
def add_truck():
    # If the user clicks the "Add Vehicle" button, this code runs:
    if request.method == 'POST':
        model = request.form['model']
        daily_rate = request.form['daily_rate']

        # We will add the raw SQL to save this to the database in the next step!
        print(f"Success: Received {model} at ${daily_rate}/day")
        return redirect(url_for('index'))

    # If the user is just visiting the page, show them the HTML form:
    return render_template('add_truck.html')

if __name__ == '__main__':
    # Uncomment the line below the first time you run this to create the DB
    # init_db()
    app.run(debug=True)