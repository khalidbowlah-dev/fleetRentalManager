import sqlite3
from flask import Flask, render_template

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

if __name__ == '__main__':
    # Uncomment the line below the first time you run this to create the DB
    init_db()
    app.run(debug=True)