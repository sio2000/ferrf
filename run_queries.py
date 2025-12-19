#!/usr/bin/env python3
"""
Execute all queries and get results for REPORT.md
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Database configuration
DB_CONFIG = {
    'host': 'db.nbohnrjmtoyrxrxqulrj.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': '10Stomathima!',
    'port': 5432
}

def execute_query(conn, query, description):
    """Execute a query and return results"""
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return [dict(row) for row in results]
    except Exception as e:
        print(f"Error executing {description}: {e}")
        return None

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    print("=" * 80)
    print("QUERY RESULTS")
    print("=" * 80)
    
    # Query A: Title contains 'rat' OR 'liver'
    print("\nQuery A: Count documents where TITLE contains 'rat' OR 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE title_tsv @@ to_tsquery('english', 'rat | liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query B: Abstract contains 'rat' OR 'liver'
    print("\nQuery B: Count documents where ABSTRACT contains 'rat' OR 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE abstract_tsv @@ to_tsquery('english', 'rat | liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query C: Title OR Abstract contains 'rat' OR 'liver'
    print("\nQuery C: Count documents where TITLE OR ABSTRACT contains 'rat' OR 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE (title_tsv || abstract_tsv) @@ to_tsquery('english', 'rat | liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query D: Title AND Abstract both contain 'rat' OR 'liver'
    print("\nQuery D: Count documents where TITLE AND ABSTRACT both contain 'rat' OR 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE title_tsv @@ to_tsquery('english', 'rat | liver') AND abstract_tsv @@ to_tsquery('english', 'rat | liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query E-A: Title contains 'rat' AND 'liver'
    print("\nQuery E-A: Count documents where TITLE contains 'rat' AND 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE title_tsv @@ to_tsquery('english', 'rat & liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query E-B: Abstract contains 'rat' AND 'liver'
    print("\nQuery E-B: Count documents where ABSTRACT contains 'rat' AND 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE abstract_tsv @@ to_tsquery('english', 'rat & liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query E-C: Title OR Abstract contains 'rat' AND 'liver'
    print("\nQuery E-C: Count documents where TITLE OR ABSTRACT contains 'rat' AND 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE (title_tsv || abstract_tsv) @@ to_tsquery('english', 'rat & liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query E-D: Title AND Abstract both contain 'rat' AND 'liver'
    print("\nQuery E-D: Count documents where TITLE AND ABSTRACT both contain 'rat' AND 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE title_tsv @@ to_tsquery('english', 'rat & liver') AND abstract_tsv @@ to_tsquery('english', 'rat & liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query F: Documents with 'cancer' AND 'liver' in abstract (count only)
    print("\nQuery F: Count documents where ABSTRACT contains 'cancer' AND 'liver'")
    cur.execute("SELECT COUNT(*) AS count FROM docs WHERE abstract_tsv @@ to_tsquery('english', 'cancer & liver');")
    result = cur.fetchone()
    print(f"Result: {result['count']}")
    
    # Query G: Top 10 terms by Document Frequency
    print("\nQuery G: Top 10 terms by Document Frequency (DF)")
    cur.execute("""
        SELECT 
            word AS term,
            ndoc AS document_frequency
        FROM ts_stat('SELECT title_tsv || abstract_tsv FROM docs WHERE title_tsv IS NOT NULL OR abstract_tsv IS NOT NULL')
        ORDER BY ndoc DESC
        LIMIT 10;
    """)
    results = cur.fetchall()
    for i, row in enumerate(results, 1):
        print(f"  {i}. {row['term']}: {row['document_frequency']}")
    
    # Query H: Top 10 terms by Collection Frequency
    print("\nQuery H: Top 10 terms by Collection Frequency (CF)")
    cur.execute("""
        SELECT 
            word AS term,
            nentry AS collection_frequency
        FROM ts_stat('SELECT title_tsv || abstract_tsv FROM docs WHERE title_tsv IS NOT NULL OR abstract_tsv IS NOT NULL')
        ORDER BY nentry DESC
        LIMIT 10;
    """)
    results = cur.fetchall()
    for i, row in enumerate(results, 1):
        print(f"  {i}. {row['term']}: {row['collection_frequency']}")
    
    # Total documents
    print("\nTotal documents in database:")
    cur.execute("SELECT COUNT(*) AS total FROM docs;")
    result = cur.fetchone()
    print(f"Result: {result['total']}")
    
    cur.close()
    conn.close()
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

