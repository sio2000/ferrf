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
    """Netlify function handler"""
    """Handle stats requests"""
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total document count
        cur.execute("SELECT COUNT(*) AS total FROM docs;")
        total = cur.fetchone()['total']
        
        # Get documents with title/abstract
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE title IS NOT NULL AND title != '') AS with_title,
                COUNT(*) FILTER (WHERE abstract IS NOT NULL AND abstract != '') AS with_abstract
            FROM docs;
        """)
        stats = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'total_documents': total,
                'with_title': stats['with_title'],
                'with_abstract': stats['with_abstract']
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

