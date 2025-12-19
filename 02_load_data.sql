-- ============================================
-- PART A: DATA LOADING FROM JSON LINES
-- ============================================
-- This script loads data from JSON Lines format (data.txt)
-- into PostgreSQL using temporary table and JSONB functionality

-- Step 1: Create temporary table for raw JSON data
DROP TABLE IF EXISTS temp_json_data CASCADE;

CREATE TEMP TABLE temp_json_data (
    json_data JSONB
);

-- Step 2: Load JSON Lines file into temporary table
-- Note: This requires the file to be accessible by PostgreSQL server
-- For Supabase, we'll use a different approach with COPY or programmatic loading
-- Alternative: Use COPY with program to read line by line

-- For local PostgreSQL with file access:
-- COPY temp_json_data(json_data) FROM PROGRAM 'cat /path/to/data.txt' (FORMAT text);

-- For Supabase/remote: We'll use a Python script or psql with \copy
-- This SQL assumes data is loaded via external script or COPY command

-- Step 3: Extract title and abstract from JSON and insert into docs table
-- Handle NULL values gracefully
INSERT INTO docs (title, abstract)
SELECT 
    COALESCE(json_data->>'title', '') AS title,
    COALESCE(json_data->>'abstract', '') AS abstract
FROM temp_json_data
WHERE json_data->>'title' IS NOT NULL 
   OR json_data->>'abstract' IS NOT NULL;

-- Step 4: Verify data loading
SELECT 
    COUNT(*) AS total_documents,
    COUNT(title) AS documents_with_title,
    COUNT(abstract) AS documents_with_abstract,
    COUNT(*) FILTER (WHERE title IS NULL OR title = '') AS missing_titles,
    COUNT(*) FILTER (WHERE abstract IS NULL OR abstract = '') AS missing_abstracts
FROM docs;

-- Clean up temporary table
DROP TABLE IF EXISTS temp_json_data;

