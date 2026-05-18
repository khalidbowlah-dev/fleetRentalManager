DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS trucks;

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
