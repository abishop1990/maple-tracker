-- Handles the insertion of a single parsed row
INSERT INTO entries (date, time, total_weight, water_weight, drink, refill_to, notes)
VALUES (?, ?, ?, ?, ?, ?, ?);