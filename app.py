#!/usr/bin/env python3
"""
Web Application for Full-Text Search
Simple Flask-based search engine over PostgreSQL docs table
"""

from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db.nbohnrjmtoyrxrxqulrj.supabase.co'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '10Stomathima!'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    """Create and return database connection"""
    return psycopg2.connect(**DB_CONFIG)

@app.route('/')
def index():
    """Main search page"""
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Perform full-text search and return ranked results"""
    
    if request.method == 'GET':
        query = request.args.get('q', '').strip()
    else:
        query = request.form.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build full-text search query
        # Use plainto_tsquery for user-friendly query parsing
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
        
        return jsonify({
            'query': query,
            'count': len(results_list),
            'results': results_list
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
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
        
        return jsonify({
            'total_documents': total,
            'with_title': stats['with_title'],
            'with_abstract': stats['with_abstract']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

