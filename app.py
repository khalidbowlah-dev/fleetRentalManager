import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

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
    # Connect to the database and grab all trucks
    db = get_db_connection()
    trucks = db.execute('SELECT * FROM trucks').fetchall()
    db.close()

    # Send those trucks to your index.html file
    return render_template('index.html', trucks=trucks)

@app.route('/add_truck', methods=['GET', 'POST'])
def add_truck():
    if request.method == 'POST':
        model = request.form['model']
        daily_rate = request.form['daily_rate']

        # Connect to DB and INSERT the new truck
        db = get_db_connection()
        db.execute('INSERT INTO trucks (owner_id, model, daily_rate) VALUES (?, ?, ?)',
                   (1, model, daily_rate))
        db.commit()
        db.close()

        return redirect(url_for('index'))

    return render_template('add_truck.html')

if __name__ == '__main__':
    # init_db()
    app.run(debug=True)