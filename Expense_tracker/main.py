import sqlite3

conn = sqlite3.connect("expense.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    amount REAL,
    category TEXT,
    date TEXT,
    description TEXT
)
""")

conn.commit()
conn.close()

def add_expense():
    amount = float(input("Enter amount: "))
    category = input("Enter category: ")
    date = input("Enter date: ")
    description = input("Enter description: ")

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, category, date, description) VALUES (?, ?, ?, ?)",
        (amount, category, date, description)
    )

    conn.commit()
    conn.close()

    print("Expense added successfully!")

    
def view_expenses():
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    print("\nID | Amount | Category | Date | Description")
    print("---------------------------------------------")

    for row in rows:
        print(row[0], "|", row[1], "|", row[2], "|", row[3], "|", row[4])

    conn.close()

def category_report():
    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)

    rows = cursor.fetchall()

    print("\nCategory-wise Spending")
    print("-----------------------")

    for row in rows:
        print(row[0], ":", row[1])

    conn.close()

while True:
    print("\n1 Add Expense")
    print("2 View Expenses")
    print("3 Category Report")
    print("4 Exit")

    choice = int(input("Enter choice: "))

    if choice == 1:
        add_expense()

    elif choice == 2:
        view_expenses()

    elif choice == 3:
        category_report()

    elif choice == 4:
        break
