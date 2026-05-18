DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS trucks;
DROP TABLE IF EXISTS users;

-- Table for customer accounts
CREATE TABLE users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL UNIQUE,
                       password TEXT NOT NULL
);

-- Table for the fleet, linked to the user who owns it
CREATE TABLE trucks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        owner_id INTEGER NOT NULL,
                        model TEXT NOT NULL,
                        daily_rate REAL NOT NULL,
                        status TEXT DEFAULT 'Available',
                        FOREIGN KEY (owner_id) REFERENCES users (id)
);
-- Table to store real truck rentals
CREATE TABLE bookings (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          truck_id INTEGER NOT NULL,
                          renter_id INTEGER NOT NULL,
                          start_date TEXT NOT NULL,
                          end_date TEXT NOT NULL,
                          total_cost REAL NOT NULL,
                          FOREIGN KEY (truck_id) REFERENCES trucks (id),
                          FOREIGN KEY (renter_id) REFERENCES users (id)
);
