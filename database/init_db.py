import sqlite3

def init_db(db_path="taotrader.db"):
    with open("sqls/init_db.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
