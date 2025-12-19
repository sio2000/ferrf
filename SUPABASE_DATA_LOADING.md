# Οδηγίες Φόρτωσης Δεδομένων στη Supabase

## Προσοχή: Τοπικό DNS Πρόβλημα

Αν το `load_data.py` δεν μπορεί να συνδεθεί λόγω DNS error, μπορείς να φορτώσεις τα δεδομένα μέσω Supabase Dashboard.

## Μέθοδος 1: Supabase SQL Editor (Συνιστάται)

1. Πήγαινε στο Supabase Dashboard: https://supabase.com/dashboard
2. Επίλεξε το project σου
3. Πήγαινε στο **SQL Editor**
4. Εκτέλεσε τα παρακάτω scripts με τη σειρά:

### Βήμα 1: Δημιουργία Σχήματος
Εκτέλεσε το `01_schema.sql` (αν δεν έχει ήδη εκτελεστεί)

### Βήμα 2: Φόρτωση Δεδομένων
Χρησιμοποίησε το Supabase Storage ή SQL Editor:

**Επιλογή A: Μέσω SQL Editor (για μικρά datasets)**
- Αν το data.txt είναι μικρό, μπορείς να το ανεβάσεις στο Supabase Storage
- Μετά χρησιμοποίησε COPY command

**Επιλογή B: Μέσω Python Script (αν λειτουργεί το DNS)**
```bash
python load_data.py
```

### Βήμα 3: Full Text Search Setup
Εκτέλεσε το `03_fts_setup.sql` για να:
- Προσθέσεις TSVECTOR columns
- Δημιουργήσεις GIN indexes
- Ρυθμίσεις triggers

## Μέθοδος 2: Supabase CLI

Αν έχεις εγκαταστήσει το Supabase CLI:

```bash
# Login
supabase login

# Link project
supabase link --project-ref nbohnrjmtoyrxrxqulrj

# Run migrations
supabase db push
```

## Μέθοδος 3: psql Command Line

Αν έχεις πρόσβαση σε psql:

```bash
# Connect to database
psql "postgresql://postgres:10Stomathima!@db.nbohnrjmtoyrxrxqulrj.supabase.co:5432/postgres"

# Then run SQL files
\i 01_schema.sql
\i 03_fts_setup.sql
```

## Credentials

- **Host:** db.nbohnrjmtoyrxrxqulrj.supabase.co
- **Database:** postgres
- **User:** postgres
- **Password:** 10Stomathima!
- **Port:** 5432
- **Connection String:** postgresql://postgres:10Stomathima!@db.nbohnrjmtoyrxrxqulrj.supabase.co:5432/postgres

## Σημείωση

Ο φάκελος `data/` είναι στο `.gitignore` και δεν θα ανέβει στο GitHub.
Τα δεδομένα πρέπει να φορτωθούν απευθείας στη βάση Supabase.

## Επαλήθευση

Μετά τη φόρτωση, εκτέλεσε στο Supabase SQL Editor:

```sql
SELECT COUNT(*) FROM docs;
SELECT COUNT(*) FROM docs WHERE title_tsv IS NOT NULL;
SELECT COUNT(*) FROM docs WHERE abstract_tsv IS NOT NULL;
```

