ALTER TABLE partners ALTER COLUMN rating TYPE INT USING ROUND(rating)::INT;
ALTER TABLE partners ALTER COLUMN rating SET DEFAULT 0;
UPDATE partners SET rating = 0 WHERE rating IS NULL;
ALTER TABLE partners ALTER COLUMN rating SET NOT NULL;
ALTER TABLE partners ADD CONSTRAINT chk_partners_rating CHECK (rating >= 0);
ALTER TABLE partners DROP CONSTRAINT IF EXISTS partners_inn_unique;