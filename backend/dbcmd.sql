-- --- START OF FILE dbcmd.sql ---
-- Create the Imagefeatures table if it doesn't exist
CREATE TABLE IF NOT EXISTS Imagefeatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    feature_type TEXT NOT NULL,
    feature_value TEXT,
    probability REAL
);

-- Create an index on the filename column for faster lookups
CREATE INDEX IF NOT EXISTS idx_filename ON Imagefeatures (filename);

-- Create an index on the feature_value column for faster lookups
CREATE INDEX IF NOT EXISTS idx_feature_value ON Imagefeatures (feature_value);

-- Create a table for storing feedback history (optional but recommended)
CREATE TABLE IF NOT EXISTS FeedbackHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    feedback TEXT,  -- "positive" or "negative"
    query TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create UserSentences table
CREATE TABLE IF NOT EXISTS UserSentences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    sentence TEXT NOT NULL
);

-- Index for UserSentences
CREATE INDEX IF NOT EXISTS idx_user_sentences_filename ON UserSentences (filename);