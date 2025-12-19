import sys
import os
import json

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db.nbohnrjmtoyrxrxqulrj.supabase.co'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '10Stomathima!'),
    'port': os.getenv('DB_PORT', '5432')
}

def handler(event, context):
    """Handle search requests"""
    try:
        # Get query parameter
        query_params = event.get('queryStringParameters') or {}
        query = query_params.get('q', '').strip()
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build full-text search query
        search_query = """
            SELECT 
                id,
                title,
                LEFT(abstract, 500) AS abstract_preview,
                ts_rank_cd(
                    (title_tsv || abstract_tsv),
                    plainto_tsquery('english', %s)
                ) AS rank
            FROM docs
            WHERE (title_tsv || abstract_tsv) @@ plainto_tsquery('english', %s)
            ORDER BY rank DESC
            LIMIT 50
        """
        
        cur.execute(search_query, (query, query))
        results = cur.fetchall()
        
        # Convert results to list of dicts
        results_list = [dict(row) for row in results]
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'query': query,
                'count': len(results_list),
                'results': results_list
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

