import sqlite3

DBFILE = 'compensation.db'

def reset_db():
    conn = sqlite3.connect(DBFILE)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS records")
    cur.execute('''CREATE TABLE records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT,
        register_number TEXT,
        survey_number TEXT,
        village TEXT,
        taluk TEXT,
        district TEXT,
        land_area TEXT,
        compensation_amount TEXT,
        fair_compensation REAL,
        fairness_passed BOOLEAN,
        date TEXT,
        raw_text TEXT,
        public_usage TEXT,
        families_affected INTEGER,
        other_properties TEXT,
        rehab_plan TEXT,
        estimated_cost REAL,
        positive_impact TEXT,
        classification_result TEXT
    )''')
    conn.commit()
    conn.close()
    print("Database reset and upgraded successfully.")

if __name__ == '__main__':
    reset_db()
