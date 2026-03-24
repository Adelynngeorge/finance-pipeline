import sqlite3

conn = sqlite3.connect('finance.db')
cur = conn.cursor()

cur.executescript('''
  CREATE TABLE IF NOT EXISTS credit_cards (
    id INTEGER PRIMARY KEY,
    name TEXT, balance REAL, apr REAL,
    min_payment REAL, credit_limit REAL
  );
  CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY,
    name TEXT, balance REAL, apr REAL,
    min_payment REAL, loan_type TEXT
  );
''')

cur.execute("INSERT INTO credit_cards VALUES (1,'Chase Sapphire',4200,22.99,120,10000)")
cur.execute("INSERT INTO loans VALUES (1,'Car Loan',9400,6.49,280,'auto')")
conn.commit()
conn.close()
print("Done! Database created.")