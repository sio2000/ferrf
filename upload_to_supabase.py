#!/usr/bin/env python3
"""
Upload data to Supabase using REST API
This script reads data.txt and uploads to Supabase via REST API
"""

import json
import requests
import sys
from pathlib import Path
from time import sleep

# Supabase configuration
SUPABASE_URL = "https://nbohnrjmtoyrxrxqulrj.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5ib2hucmptdG95cnhyeHF1bHJqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjE1Njg0MSwiZXhwIjoyMDgxNzMyODQxfQ.S4SjIgGtaLS5SxlZBpPXKIeYM28tb3HIMZB2xdIEa_8"

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

def upload_batch(batch):
    """Upload a batch of documents to Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/docs"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    try:
        response = requests.post(url, json=batch, headers=headers)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"Error uploading batch: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Exception uploading batch: {e}")
        return False

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
    
    # Prepare batches
    batch = []
    total_uploaded = 0
    batch_size = 100
    
    print("Uploading data to Supabase via REST API...")
    print("Note: This may take a while for large files...")
    
    for json_obj in load_json_lines(json_file):
        title = json_obj.get('title', '') or ''
        abstract = json_obj.get('abstract', '') or ''
        
        if title or abstract:
            batch.append({
                'title': title,
                'abstract': abstract
            })
            
            if len(batch) >= batch_size:
                if upload_batch(batch):
                    total_uploaded += len(batch)
                    print(f"Uploaded {total_uploaded:,} documents...", end='\r')
                else:
                    print(f"\nFailed to upload batch at {total_uploaded}")
                    break
                batch = []
                sleep(0.1)  # Rate limiting
    
    # Upload remaining
    if batch:
        if upload_batch(batch):
            total_uploaded += len(batch)
    
    print(f"\n✓ Total documents uploaded: {total_uploaded:,}")
    print("✓ Data upload completed!")
    print("\nNext step: Run 03_fts_setup.sql in Supabase SQL Editor")

if __name__ == '__main__':
    main()

