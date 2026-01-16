import sqlite3

DB_FILE = "compensation.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_name TEXT,
        register_number TEXT,
        survey_number TEXT UNIQUE,
        village TEXT,
        taluk TEXT,
        district TEXT,
        land_area TEXT,
        compensation_amount TEXT,
        date TEXT,
        raw_text TEXT,
        public_usage TEXT,
        families_affected INTEGER,
        other_properties TEXT,
        rehab_plan TEXT,
        estimated_cost REAL,
        positive_impact TEXT,
        fair_compensation REAL,
        fairness_passed BOOLEAN,
        classification_result TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_record(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO records (
            owner_name, register_number, survey_number, village, taluk, district,
            land_area, compensation_amount, date, raw_text,
            public_usage, families_affected, other_properties,
            rehab_plan, estimated_cost, positive_impact,
            fair_compensation, fairness_passed, classification_result
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("owner_name", ""),
            data.get("register_number", ""),
            data.get("survey_number", ""),
            data.get("village", ""),
            data.get("taluk", ""),
            data.get("district", ""),
            data.get("land_area", ""),
            data.get("compensation_amount", ""),
            data.get("date", ""),
            data.get("raw_text", ""),
            data.get("public_usage", ""),
            data.get("families_affected", 0),
            data.get("other_properties", ""),
            data.get("rehab_plan", ""),
            data.get("estimated_cost", 0.0),
            data.get("positive_impact", ""),
            data.get("fair_compensation", 0.0),
            data.get("fairness_passed", False),
            data.get("classification_result", "")
        ))
        conn.commit()
        return True, "Inserted successfully"
    except sqlite3.IntegrityError:
        return False, f"Survey No {data.get('survey_number', '')} already exists"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_impact(data):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("""
        UPDATE records
        SET public_usage = ?,
            families_affected = ?,
            other_properties = ?,
            rehab_plan = ?,
            estimated_cost = ?,
            positive_impact = ?
        WHERE survey_number = ?
        """, (
            data.get("public_usage", ""),
            data.get("families_affected", 0),
            data.get("other_properties", ""),
            data.get("rehab_plan", ""),
            data.get("estimated_cost", 0.0),
            data.get("positive_impact", ""),
            data.get("survey_number", ""),
        ))
        conn.commit()
        if cur.rowcount == 0:
            return False, "No record found for that survey_number"
        return True, "Impact details updated successfully"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_all_records():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM records ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_record_by_survey_number(survey_number):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM records WHERE survey_number = ?", (survey_number,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
