-- Handles updating an existing entry by ID
UPDATE entries
SET date         = ?,
    time         = ?,
    total_weight = ?,
    water_weight = ?,
    drink        = ?,
    refill_to    = ?,
    notes        = ?,
    updated_at   = CURRENT_TIMESTAMP
WHERE id = ?;