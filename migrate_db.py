
import sqlite3
import os

database_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "cryptolife.db"
)

connection = sqlite3.connect(database_path)
cursor = connection.cursor()

# Check whether the paper table exists
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='table' AND name='paper'
""")

if cursor.fetchone() is None:
    print("Paper table does not exist in this database.")
else:
    columns = [
        row[1]
        for row in cursor.execute(
            "PRAGMA table_info(paper)"
        ).fetchall()
    ]

    if "journal" not in columns:
        cursor.execute(
            "ALTER TABLE paper ADD COLUMN journal VARCHAR(300)"
        )
        print("Journal column added successfully.")
    else:
        print("Journal column already exists.")

connection.commit()
connection.close()
