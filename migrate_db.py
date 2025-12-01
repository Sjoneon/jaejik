# migrate_db.py
# DB migration script
# Run: python migrate_db.py

import sqlite3

print("=" * 50)
print("DB Migration Start")
print("=" * 50)

conn = sqlite3.connect('database/app.db')
cursor = conn.cursor()

print("\n[1] Adding columns to users table...")

try:
    cursor.execute('ALTER TABLE users ADD COLUMN company_id INTEGER')
    print("  OK: company_id added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: company_id exists")
    else:
        print("  ERROR:", e)

try:
    cursor.execute('ALTER TABLE users ADD COLUMN team_id INTEGER')
    print("  OK: team_id added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: team_id exists")
    else:
        print("  ERROR:", e)

try:
    cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'member'")
    print("  OK: role added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: role exists")
    else:
        print("  ERROR:", e)

print("\n[2] Adding columns to schedules table...")

try:
    cursor.execute('ALTER TABLE schedules ADD COLUMN start_date DATE')
    print("  OK: start_date added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: start_date exists")
    else:
        print("  ERROR:", e)

try:
    cursor.execute('ALTER TABLE schedules ADD COLUMN start_time TIME')
    print("  OK: start_time added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: start_time exists")
    else:
        print("  ERROR:", e)

try:
    cursor.execute('ALTER TABLE schedules ADD COLUMN end_time TIME')
    print("  OK: end_time added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: end_time exists")
    else:
        print("  ERROR:", e)

try:
    cursor.execute('ALTER TABLE schedules ADD COLUMN is_all_day BOOLEAN DEFAULT 1')
    print("  OK: is_all_day added")
except sqlite3.OperationalError as e:
    if "duplicate column" in str(e).lower():
        print("  SKIP: is_all_day exists")
    else:
        print("  ERROR:", e)

print("\n[3] Creating companies table...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(200),
    admin_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')
print("  OK: companies table ready")

print("\n[4] Creating teams table...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(200),
    leader_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)
''')
print("  OK: teams table ready")

print("\n[5] Updating existing schedules (set start_date = due_date where NULL)...")
cursor.execute('UPDATE schedules SET start_date = due_date WHERE start_date IS NULL')
print("  OK: existing schedules updated")

conn.commit()
conn.close()

print("\n" + "=" * 50)
print("Migration Complete!")
print("=" * 50)
print("\nNow run: python app.py")
