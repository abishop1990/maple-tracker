-- Initializes the core table structure
CREATE TABLE IF NOT EXISTS settings
(
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries
(
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    date         TEXT    NOT NULL CHECK (date LIKE '____-__-__'),
    time         TEXT    NOT NULL CHECK (time LIKE '__:__'),
    total_weight INTEGER NOT NULL,
    water_weight INTEGER NOT NULL,
    drink        INTEGER   DEFAULT 0,
    refill_to    INTEGER,
    notes        TEXT      DEFAULT '',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_entries_date ON entries (date);