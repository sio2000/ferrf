# Οδηγίες Φόρτωσης Δεδομένων

## Προαπαιτούμενα

1. Βεβαιώσου ότι έχεις εγκαταστήσει:
   - Python 3.x
   - psycopg2-binary: `pip install psycopg2-binary`

2. Βεβαιώσου ότι ο φάκελος `data` περιέχει το αρχείο `data.txt`

## Βήματα Φόρτωσης

### 1. Εκτέλεση SQL Scripts

Εκτέλεσε τα SQL scripts με τη σειρά:

```bash
# 1. Δημιουργία σχήματος
psql -h db.nbohnrjmtoyrxrxqulrj.supabase.co -U postgres -d postgres -f 01_schema.sql

# 2. Φόρτωση δεδομένων (χρησιμοποίησε το Python script)
python load_data.py

# 3. Ρύθμιση Full Text Search
psql -h db.nbohnrjmtoyrxrxqulrj.supabase.co -U postgres -d postgres -f 03_fts_setup.sql
```

### 2. Εναλλακτικά: Χρήση Python Script

```bash
python load_data.py
```

Αυτό θα:
- Συνδεθεί στη βάση Supabase
- Φορτώσει τα δεδομένα από `data/data.txt`
- Εισάγει τα δεδομένα στον πίνακα `docs`

### 3. Επαλήθευση

Μετά τη φόρτωση, εκτέλεσε:

```bash
python run_queries.py
```

Αυτό θα εκτελέσει όλα τα queries και θα δείξει τα αποτελέσματα.

## Credentials

- **Host:** db.nbohnrjmtoyrxrxqulrj.supabase.co
- **Database:** postgres
- **User:** postgres
- **Password:** 10Stomathima!
- **Port:** 5432

## Σημείωση

Ο φάκελος `data/` είναι στο `.gitignore` και δεν θα ανέβει στο GitHub. 
Τα δεδομένα πρέπει να φορτωθούν απευθείας στη βάση Supabase.

