#!/usr/bin/env python3
"""
Test database connection with different methods
"""

import psycopg2
import socket

# Test different hostname formats
hostnames = [
    'db.nbohnrjmtoyrxrxqulrj.supabase.co',
    'nbohnrjmtoyrxrxqulrj.supabase.co',
    'aws-0-eu-central-1.pooler.supabase.com',
]

print("Testing DNS resolution...")
for hostname in hostnames:
    try:
        # Try IPv4
        try:
            ip = socket.gethostbyname(hostname)
            print(f"OK {hostname} -> IPv4: {ip}")
        except:
            # Try IPv6
            addrinfo = socket.getaddrinfo(hostname, 5432)
            if addrinfo:
                print(f"OK {hostname} -> {addrinfo[0][4]}")
    except Exception as e:
        print(f"FAIL {hostname} -> {e}")

print("\nTesting database connections...")
DB_CONFIG = {
    'database': 'postgres',
    'user': 'postgres',
    'password': '10Stomathima!',
    'port': 5432
}

for hostname in hostnames:
    try:
        config = {**DB_CONFIG, 'host': hostname}
        conn = psycopg2.connect(**config, connect_timeout=5)
        print(f"✓ Connected to {hostname}")
        cur = conn.cursor()
        cur.execute("SELECT version();")
        print(f"  PostgreSQL version: {cur.fetchone()[0][:50]}...")
        cur.close()
        conn.close()
        break
    except Exception as e:
        print(f"✗ {hostname} -> {str(e)[:100]}")

