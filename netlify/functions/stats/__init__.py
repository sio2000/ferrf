import sys
import os
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration - using connection string for better compatibility
DB_CONNECTION_STRING = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:10Stomathima!@db.nbohnrjmtoyrxrxqulrj.supabase.co:5432/postgres'
)

# Fallback to individual parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db.nbohnrjmtoyrxrxqulrj.supabase.co'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '10Stomathima!'),
    'port': os.getenv('DB_PORT', '5432')
}

def handler(event, context):
    """Netlify function handler for stats requests"""
    logger.info(f"Stats function called")
    try:
        # Connect to database
        logger.info("Connecting to database...")
        try:
            conn = psycopg2.connect(DB_CONNECTION_STRING)
        except Exception as e:
            logger.warning(f"Connection string failed: {e}, trying individual parameters")
            conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        logger.info("Database connection established")
        
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
        
        response = {
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
        logger.info(f"Stats retrieved successfully: total={total}, with_title={stats['with_title']}, with_abstract={stats['with_abstract']}")
        return response
    
    except Exception as e:
        logger.error(f"Error in stats function: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

