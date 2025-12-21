-- Create RPC function for full-text search
CREATE OR REPLACE FUNCTION search_docs(search_query TEXT)
RETURNS TABLE (
  id INTEGER,
  title TEXT,
  abstract_preview TEXT,
  rank REAL
) 
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.id,
    d.title,
    LEFT(d.abstract, 500) AS abstract_preview,
    ts_rank_cd(
      (d.title_tsv || d.abstract_tsv),
      plainto_tsquery('english', search_query)
    )::REAL AS rank
  FROM docs d
  WHERE (d.title_tsv || d.abstract_tsv) @@ plainto_tsquery('english', search_query)
  ORDER BY rank DESC
  LIMIT 50;
END;
$$;

-- Create RPC function for document count
CREATE OR REPLACE FUNCTION count_docs()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
  total_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO total_count FROM docs;
  RETURN total_count;
END;
$$;

-- Grant execute permissions to anon role (for REST API)
GRANT EXECUTE ON FUNCTION search_docs(TEXT) TO anon;
GRANT EXECUTE ON FUNCTION count_docs() TO anon;

