#!/usr/bin/env python3
"""
Data Loading Script for PostgreSQL
Loads JSON Lines file (data.txt) into PostgreSQL database
"""

import json
import psycopg2
import sys
import os
from psycopg2.extras import execute_batch
from pathlib import Path
import socket

# Database connection parameters
# Supabase connection string (from Supabase dashboard > Settings > Database > Connection string)
# Format: postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
DB_CONNECTION_STRING = 'postgresql://postgres:10Stomathima!@db.nbohnrjmtoyrxrxqulrj.supabase.co:5432/postgres'

# Alternative: Individual parameters (fallback)
DB_CONFIG = {
    'host': 'db.nbohnrjmtoyrxrxqulrj.supabase.co',
    'database': 'postgres',
    'user': 'postgres',
    'password': '10Stomathima!',
    'port': 5432
}

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

def load_data_to_postgres(json_file_path, batch_size=1000):
    """Load JSON Lines data into PostgreSQL docs table"""
    
    # Test DNS resolution first (supports both IPv4 and IPv6)
    hostname = 'db.nbohnrjmtoyrxrxqulrj.supabase.co'
    print(f"Testing DNS resolution for {hostname}...")
    try:
        # Try IPv4 first
        try:
            ip = socket.gethostbyname(hostname)
            print(f"DNS resolved to IPv4: {ip}")
        except socket.gaierror:
            # Try IPv6
            addrinfo = socket.getaddrinfo(hostname, 5432, socket.AF_INET6)
            if addrinfo:
                print(f"DNS resolved to IPv6: {addrinfo[0][4][0]}")
    except Exception as e:
        print(f"DNS resolution info: {e}")
        print("Trying to connect anyway (psycopg2 handles DNS)...")
    
    # Connect to database - try multiple methods
    conn = None
    try:
        # Try pooler connection first (most reliable)
        try:
            print("Trying pooler connection...")
            conn = psycopg2.connect(DB_CONNECTION_STRING_POOLER, connect_timeout=10)
            print("✓ Connected using pooler connection")
        except Exception as e1:
            print(f"Pooler failed: {e1}")
            # Try direct connection string
            try:
                print("Trying direct connection string...")
                conn = psycopg2.connect(DB_CONNECTION_STRING, connect_timeout=10)
                print("✓ Connected using direct connection string")
            except Exception as e2:
                print(f"Direct connection failed: {e2}")
                # Fallback to individual parameters
                print("Trying individual parameters...")
                conn = psycopg2.connect(**DB_CONFIG, connect_timeout=10)
                print("✓ Connected using individual parameters")
        cur = conn.cursor()
    except Exception as e:
        print(f"\n❌ Error connecting to database: {e}", file=sys.stderr)
        print("\nTroubleshooting:", file=sys.stderr)
        print("1. Check your internet connection", file=sys.stderr)
        print("2. Try: ipconfig /flushdns (in PowerShell as Administrator)", file=sys.stderr)
        print("3. Verify Supabase project is active", file=sys.stderr)
        print("4. Try using Supabase SQL Editor to verify connection", file=sys.stderr)
        sys.exit(1)
    
    # Clear existing data (optional - comment out if you want to append)
    cur.execute("TRUNCATE TABLE docs RESTART IDENTITY CASCADE;")
    print("Cleared existing data from docs table")
    
    # Prepare insert statement
    insert_query = """
        INSERT INTO docs (title, abstract)
        VALUES (%s, %s)
    """
    
    # Load data in batches
    batch = []
    total_inserted = 0
    
    print(f"Loading data from {json_file_path}...")
    
    for json_obj in load_json_lines(json_file_path):
        title = json_obj.get('title', '')
        abstract = json_obj.get('abstract', '')
        
        # Only insert if at least one field is not empty
        if title or abstract:
            batch.append((title, abstract))
            
            # Insert batch when it reaches batch_size
            if len(batch) >= batch_size:
                execute_batch(cur, insert_query, batch)
                conn.commit()
                total_inserted += len(batch)
                print(f"Inserted {total_inserted} documents...", end='\r')
                batch = []
    
    # Insert remaining records
    if batch:
        execute_batch(cur, insert_query, batch)
        conn.commit()
        total_inserted += len(batch)
    
    print(f"\nTotal documents inserted: {total_inserted}")
    
    # Verify insertion
    cur.execute("SELECT COUNT(*) FROM docs;")
    count = cur.fetchone()[0]
    print(f"Total documents in database: {count}")
    
    # Close connection
    cur.close()
    conn.close()
    print("Data loading completed successfully!")

if __name__ == '__main__':
    # Try data/data.txt first, then data.txt in root
    json_file = Path('data/data.txt')
    if not json_file.exists():
        json_file = Path('data.txt')
    
    if not json_file.exists():
        print(f"Error: {json_file} not found!", file=sys.stderr)
        print("Looking for data/data.txt or data.txt", file=sys.stderr)
        print(f"Current directory: {os.getcwd()}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Loading data from: {json_file}")
    print(f"File size: {json_file.stat().st_size / (1024*1024):.2f} MB")
    load_data_to_postgres(json_file)

