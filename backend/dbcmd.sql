CREATE TABLE Imagefeatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    feature_type TEXT NOT NULL,  -- e.g., 'color', 'CNN', 'metadata'
    feature_value BLOB,          -- Store feature values, could be a string or binary data
    probability REAL,            -- Optional: Store probability associated with the feature
    UNIQUE (filename, feature_type)
);

INSERT INTO Imagefeatures (filename, feature_type, feature_value, probability)
VALUES ('image1.jpg', 'color', 'average_color_value', 0.9);