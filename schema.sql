DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS trucks;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT UNIQUE NOT NULL,
                       password TEXT NOT NULL
);

CREATE TABLE trucks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model TEXT NOT NULL,
                        daily_rate REAL NOT NULL,
                        owner_id INTEGER NOT NULL,
                        is_maintenance BOOLEAN DEFAULT 0,
                        FOREIGN KEY (owner_id) REFERENCES users (id)
);

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