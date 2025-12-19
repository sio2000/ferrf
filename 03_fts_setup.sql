-- ============================================
-- PART B: FULL TEXT SEARCH SETUP
-- ============================================
-- This script adds TSVECTOR columns and creates GIN indexes
-- for efficient full-text search

-- Step 1: Add TSVECTOR columns to docs table
ALTER TABLE docs 
ADD COLUMN IF NOT EXISTS title_tsv TSVECTOR,
ADD COLUMN IF NOT EXISTS abstract_tsv TSVECTOR;

-- Step 2: Populate TSVECTOR columns using to_tsvector() with English configuration
-- Update existing rows
UPDATE docs
SET 
    title_tsv = to_tsvector('english', COALESCE(title, '')),
    abstract_tsv = to_tsvector('english', COALESCE(abstract, ''))
WHERE title_tsv IS NULL OR abstract_tsv IS NULL;

-- Step 3: Create trigger function to automatically update TSVECTOR columns
-- when title or abstract is inserted/updated
CREATE OR REPLACE FUNCTION update_docs_tsvector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.title_tsv := to_tsvector('english', COALESCE(NEW.title, ''));
    NEW.abstract_tsv := to_tsvector('english', COALESCE(NEW.abstract, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Create trigger to automatically update TSVECTOR on insert/update
DROP TRIGGER IF EXISTS docs_tsvector_update ON docs;

CREATE TRIGGER docs_tsvector_update
    BEFORE INSERT OR UPDATE ON docs
    FOR EACH ROW
    EXECUTE FUNCTION update_docs_tsvector();

-- Step 5: Create GIN indexes for efficient full-text search
-- GIN (Generalized Inverted Index) is optimal for TSVECTOR columns
CREATE INDEX IF NOT EXISTS idx_docs_title_tsv ON docs USING GIN (title_tsv);
CREATE INDEX IF NOT EXISTS idx_docs_abstract_tsv ON docs USING GIN (abstract_tsv);

-- Step 6: Create composite index for combined title+abstract searches
CREATE INDEX IF NOT EXISTS idx_docs_combined_tsv ON docs 
USING GIN ((title_tsv || abstract_tsv));

-- Step 7: Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'docs'
ORDER BY indexname;

-- Step 8: Analyze table for query optimization
ANALYZE docs;

