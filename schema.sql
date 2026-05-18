-- Drop tables if they exist so you can easily reset your database
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS trucks;
DROP TABLE IF EXISTS users;

-- 1. Users Table (For Authentication)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- 2. Trucks Table (For Inventory - Linked to User)
CREATE TABLE trucks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    model TEXT NOT NULL,
    daily_rate REAL NOT NULL,
    status TEXT DEFAULT 'Available',
    FOREIGN KEY (owner_id) REFERENCES users (id)
);

-- 3. Bookings Table (For the Booking Engine)
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    truck_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_cost REAL NOT NULL,
    FOREIGN KEY (truck_id) REFERENCES trucks (id)
);
