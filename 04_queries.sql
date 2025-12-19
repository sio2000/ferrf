-- ============================================
-- PART B: REQUIRED QUERIES
-- ============================================
-- All queries use PostgreSQL Full Text Search operators
-- (@@, to_tsquery, plainto_tsquery, ts_rank_cd, etc.)

-- ============================================
-- QUERIES A-D: 'rat' OR 'liver'
-- ============================================

-- Query A: Count documents where TITLE contains 'rat' OR 'liver'
SELECT COUNT(*) AS count_title_rat_or_liver
FROM docs
WHERE title_tsv @@ to_tsquery('english', 'rat | liver');

-- Query B: Count documents where ABSTRACT contains 'rat' OR 'liver'
SELECT COUNT(*) AS count_abstract_rat_or_liver
FROM docs
WHERE abstract_tsv @@ to_tsquery('english', 'rat | liver');

-- Query C: Count documents where TITLE OR ABSTRACT contains 'rat' OR 'liver'
SELECT COUNT(*) AS count_title_or_abstract_rat_or_liver
FROM docs
WHERE (title_tsv || abstract_tsv) @@ to_tsquery('english', 'rat | liver');

-- Query D: Count documents where TITLE AND ABSTRACT both contain 'rat' OR 'liver'
-- Note: This means (title has rat OR liver) AND (abstract has rat OR liver)
SELECT COUNT(*) AS count_title_and_abstract_rat_or_liver
FROM docs
WHERE title_tsv @@ to_tsquery('english', 'rat | liver')
  AND abstract_tsv @@ to_tsquery('english', 'rat | liver');

-- ============================================
-- QUERIES E: 'rat' AND 'liver' (repeating A-D)
-- ============================================

-- Query E-A: Count documents where TITLE contains 'rat' AND 'liver'
SELECT COUNT(*) AS count_title_rat_and_liver
FROM docs
WHERE title_tsv @@ to_tsquery('english', 'rat & liver');

-- Query E-B: Count documents where ABSTRACT contains 'rat' AND 'liver'
SELECT COUNT(*) AS count_abstract_rat_and_liver
FROM docs
WHERE abstract_tsv @@ to_tsquery('english', 'rat & liver');

-- Query E-C: Count documents where TITLE OR ABSTRACT contains 'rat' AND 'liver'
SELECT COUNT(*) AS count_title_or_abstract_rat_and_liver
FROM docs
WHERE (title_tsv || abstract_tsv) @@ to_tsquery('english', 'rat & liver');

-- Query E-D: Count documents where TITLE AND ABSTRACT both contain 'rat' AND 'liver'
SELECT COUNT(*) AS count_title_and_abstract_rat_and_liver
FROM docs
WHERE title_tsv @@ to_tsquery('english', 'rat & liver')
  AND abstract_tsv @@ to_tsquery('english', 'rat & liver');

-- ============================================
-- QUERY F: Retrieve documents with ranking
-- ============================================

-- Query F: Retrieve ALL documents whose ABSTRACT contains 'cancer' AND 'liver'
-- Rank results using ts_rank_cd and order by descending rank
SELECT 
    id,
    title,
    LEFT(abstract, 200) AS abstract_preview,
    ts_rank_cd(abstract_tsv, to_tsquery('english', 'cancer & liver')) AS rank
FROM docs
WHERE abstract_tsv @@ to_tsquery('english', 'cancer & liver')
ORDER BY rank DESC;

-- ============================================
-- QUERY G: TOP 10 TERMS by Document Frequency (DF)
-- ============================================

-- Document Frequency: Number of documents containing the term
-- We extract all terms from both title_tsv and abstract_tsv
WITH all_terms AS (
    SELECT unnest(string_to_array((title_tsv || abstract_tsv)::text, ' ')) AS term
    FROM docs
    WHERE title_tsv IS NOT NULL OR abstract_tsv IS NOT NULL
),
term_stats AS (
    SELECT 
        term,
        COUNT(DISTINCT term) AS document_frequency
    FROM all_terms
    WHERE term IS NOT NULL AND term != ''
    GROUP BY term
)
SELECT 
    term,
    document_frequency AS df
FROM term_stats
ORDER BY document_frequency DESC
LIMIT 10;

-- Alternative approach using ts_stat for better accuracy
SELECT 
    word AS term,
    ndoc AS document_frequency
FROM ts_stat('SELECT title_tsv || abstract_tsv FROM docs WHERE title_tsv IS NOT NULL OR abstract_tsv IS NOT NULL')
ORDER BY ndoc DESC
LIMIT 10;

-- ============================================
-- QUERY H: TOP 10 TERMS by Collection Frequency (CF)
-- ============================================

-- Collection Frequency: Total number of occurrences of the term across all documents
SELECT 
    word AS term,
    nentry AS collection_frequency
FROM ts_stat('SELECT title_tsv || abstract_tsv FROM docs WHERE title_tsv IS NOT NULL OR abstract_tsv IS NOT NULL')
ORDER BY nentry DESC
LIMIT 10;

