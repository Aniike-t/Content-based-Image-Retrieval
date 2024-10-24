CREATE TABLE IF NOT EXISTS Imagefeatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    feature_type TEXT NOT NULL,  -- e.g., 'color', 'CNN', 'metadata'
    feature_value BLOB,          -- Store feature values, could be a string or binary data
    probability REAL           -- Optional: Store probability associated with the feature
);

CREATE TABLE IF NOT EXISTS ImageHashes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filehash TEXT NOT NULL,  -- Store hash of the file (e.g., MD5, SHA256)
    uuid TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,   -- Store the hashed password
    uuid TEXT NOT NULL UNIQUE,              -- Store the UUID for the user
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Account creation timestamp
    unique_key TEXT NOT NULL         -- Key made up of account creation time and UUID
);

