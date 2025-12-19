#!/usr/bin/env python3
"""
Simplified data loading script - uses connection string directly
"""

import json
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import sys

# Supabase connection string (from dashboard)
CONNECTION_STRING = 'postgresql://postgres:10Stomathima!@db.nbohnrjmtoyrxrxqulrj.supabase.co:5432/postgres'

def load_json_lines(file_path):
    """Load JSON Lines file and yield parsed JSON objects"""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}", file=sys.stderr)
                continue

def main():
    # Find data file
    json_file = Path('data/data.txt')
    if not json_file.exists():
        json_file = Path('data.txt')
    
    if not json_file.exists():
        print(f"Error: {json_file} not found!", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading data from: {json_file}")
    print(f"File size: {json_file.stat().st_size / (1024*1024):.2f} MB")
    
    # Connect to database
    try:
        print("Connecting to Supabase...")
        conn = psycopg2.connect(CONNECTION_STRING, connect_timeout=30)
        cur = conn.cursor()
        print("✓ Connected to database")
    except Exception as e:
        print(f"❌ Error connecting: {e}", file=sys.stderr)
        print("\n💡 Solutions:", file=sys.stderr)
        print("1. Check internet connection", file=sys.stderr)
        print("2. Try: ipconfig /flushdns (as Administrator)", file=sys.stderr)
        print("3. Use Supabase SQL Editor to load data manually", file=sys.stderr)
        print("4. See SUPABASE_DATA_LOADING.md for instructions", file=sys.stderr)
        sys.exit(1)
    
    # Clear existing data
    try:
        cur.execute("TRUNCATE TABLE docs RESTART IDENTITY CASCADE;")
        conn.commit()
        print("✓ Cleared existing data")
    except Exception as e:
        print(f"Note: Could not truncate (may not exist): {e}")
        conn.rollback()
    
    # Prepare insert
    insert_query = """
        INSERT INTO docs (title, abstract)
        VALUES (%s, %s)
    """
    
    # Load in batches
    batch = []
    total_inserted = 0
    batch_size = 1000
    
    print("Loading data...")
    for json_obj in load_json_lines(json_file):
        title = json_obj.get('title', '') or ''
        abstract = json_obj.get('abstract', '') or ''
        
        if title or abstract:
            batch.append((title, abstract))
            
            if len(batch) >= batch_size:
                execute_batch(cur, insert_query, batch)
                conn.commit()
                total_inserted += len(batch)
                print(f"Inserted {total_inserted:,} documents...", end='\r')
                batch = []
    
    # Insert remaining
    if batch:
        execute_batch(cur, insert_query, batch)
        conn.commit()
        total_inserted += len(batch)
    
    print(f"\n✓ Total documents inserted: {total_inserted:,}")
    
    # Verify
    cur.execute("SELECT COUNT(*) FROM docs;")
    count = cur.fetchone()[0]
    print(f"✓ Total documents in database: {count:,}")
    
    cur.close()
    conn.close()
    print("✓ Data loading completed!")

if __name__ == '__main__':
    main()

