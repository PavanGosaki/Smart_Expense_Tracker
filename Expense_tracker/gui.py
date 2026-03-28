import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import date
import matplotlib.pyplot as plt
import pandas as pd
from tkcalendar import DateEntry
from tkinter import messagebox

# ---------- DATABASE SETUP ----------
category_list = [
    "Food",
    "Travel",
    "Shopping",
    "Rent",
    "Bills",
    "Entertainment",
    "Health",
    "Other"
]

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

# ---------- FUNCTIONS ----------

def add_expense():

    amount = entry_amount.get()
    category = entry_category.get()
    description = entry_desc.get()
    selected_date = entry_date.get()

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO expenses (amount, category, date, description) VALUES (?, ?, ?, ?)",
        (amount, category, selected_date, description)
    )

    conn.commit()
    conn.close()
    status_label.config(text="Expense added successfully ✔")
    view_expenses()

def update_total():

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    conn.close()

    if total is None:
        total = 0

    total_label.config(text=f"Total Expenses: ₹{total:,.0f}")

# def view_expenses():

#     for row in tree.get_children():
#         tree.delete(row)

#     conn = sqlite3.connect("expense.db")
#     cursor = conn.cursor()

#     cursor.execute("SELECT * FROM expenses")
#     rows = cursor.fetchall()

#     for index, row in enumerate(rows):
#         if index % 2 == 0:
#             tree.insert("", tk.END, values=row, tags=("evenrow",))
#         else:
#             tree.insert("", tk.END, values=row, tags=("oddrow",))

#     update_total()
#     summary_label.config(text=f"Records: {len(rows)}")

def view_expenses():

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    for index, row in enumerate(rows):

        if index % 2 == 0:
            tree.insert("", tk.END, values=row, tags=("evenrow",))
        else:
            tree.insert("", tk.END, values=row, tags=("oddrow",))

    conn.close()

    update_total()
    update_summary()

    summary_label.config(text=f"Records: {len(rows)}")


def delete_expense():

    selected = tree.focus()

    if not selected:
        messagebox.showwarning("Warning", "Please select a record to delete")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this expense?"
    )

    if not confirm:
        return

    values = tree.item(selected, "values")
    expense_id = values[0]

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))

    conn.commit()
    conn.close()
    status_label.config(text="Expense deleted ✔")
    view_expenses()

def update_expense():

    selected = tree.focus()

    if not selected:
        return

    values = tree.item(selected, "values")
    expense_id = values[0]

    amount = entry_amount.get()
    category = entry_category.get()
    description = entry_desc.get()

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE expenses
    SET amount=?, category=?, description=?
    WHERE id=?
    """, (amount, category, description, expense_id))

    conn.commit()
    conn.close()
    view_expenses()
    status_label.config(text="Expense updated ✔")



def search_expense():

    category = search_category.get()

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    if category == "":
        cursor.execute("SELECT * FROM expenses")
    else:
        cursor.execute("SELECT * FROM expenses WHERE category=?", (category,))

    rows = cursor.fetchall()

    for index, row in enumerate(rows):

        if index % 2 == 0:
            tree.insert("", tk.END, values=row, tags=("evenrow",))
        else:
            tree.insert("", tk.END, values=row, tags=("oddrow",))

    conn.close()

    summary_label.config(text=f"Records: {len(rows)}")
def export_excel():

    conn = sqlite3.connect("expense.db")

    df = pd.read_sql_query("SELECT * FROM expenses", conn)

    df.to_excel("expenses.xlsx", index=False)

    conn.close()
    status_label.config(text="Expenses exported to Excel ✔")
    print("Exported to Excel")

def refresh_table():

    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)

    conn.close()

def show_dashboard():

    plt.close('all')   # close previous charts

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    """)
    category_data = cursor.fetchall()

    cursor.execute("""
    SELECT strftime('%Y-%m', date), SUM(amount)
    FROM expenses
    GROUP BY strftime('%Y-%m', date)
    """)
    monthly_data = cursor.fetchall()

    conn.close()

    categories = [row[0] for row in category_data]
    amounts = [row[1] for row in category_data]

    months = [row[0] for row in monthly_data]
    month_amounts = [row[1] for row in monthly_data]

    fig, axs = plt.subplots(2, 2, figsize=(10,8))

    axs[0,0].barh(categories, amounts)
    axs[0,0].set_title("Total Spend by Category")

    axs[0,1].plot(months, month_amounts, marker='o')
    axs[0,1].set_title("Monthly Expenses")

    axs[1,0].pie(amounts, labels=categories, autopct='%1.1f%%')
    axs[1,0].set_title("Expense Breakdown")

    axs[1,1].axis("off")

    plt.tight_layout()
    plt.show()

def select_record(event):

    selected = tree.focus()
    values = tree.item(selected, "values")

    if not values:
        return

    entry_amount.delete(0, tk.END)
    entry_amount.insert(0, values[1])

    entry_category.delete(0, tk.END)
    entry_category.insert(0, values[2])

    entry_desc.delete(0, tk.END)
    entry_desc.insert(0, values[4])

    entry_date.set_date(values[3])

def clear_fields():

    entry_amount.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_desc.delete(0, tk.END)

def sort_column(tree, col, reverse):

    data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

    # numeric sort for amount
    if col == "Amount":
        data_list.sort(key=lambda t: float(t[0]), reverse=reverse)
    else:
        data_list.sort(reverse=reverse)

    for index, (val, k) in enumerate(data_list):
        tree.move(k, '', index)

    # add arrow indicator
    if reverse:
        tree.heading(col, text=f"{col} ↓",
                     command=lambda: sort_column(tree, col, False))
    else:
        tree.heading(col, text=f"{col} ↑",
                     command=lambda: sort_column(tree, col, True))
    
def update_summary():

    conn = sqlite3.connect("expense.db")
    cursor = conn.cursor()

    # total
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]

    # today
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE date = DATE('now')")
    today = cursor.fetchone()[0]

    # month
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
        WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
    """)
    month = cursor.fetchone()[0]

    conn.close()

    total = total if total else 0
    today = today if today else 0
    month = month if month else 0

    total_card.config(text=f"Total\n₹{total:,.0f}")
    today_card.config(text=f"Today\n₹{today:,.0f}")
    month_card.config(text=f"This Month\n₹{month:,.0f}")

# -----------------   Updated GUI    -----------------

root = tk.Tk()
root.title("Smart Expense Tracker")
root.geometry("950x650")

title = tk.Label(root, text="Smart Expense Tracker", font=("Arial", 22, "bold"))
title.pack(pady=15)
root.configure(bg="#f5f5f5")


# ---------- SUMMARY CARDS ----------

summary_frame = tk.Frame(root)
summary_frame.pack(pady=10)

total_card = tk.Label(
    summary_frame,
    text="Total\n₹0",
    font=("Arial", 14, "bold"),
    bg="#4CAF50",
    fg="white",
    width=15,
    height=2
)
total_card.grid(row=0, column=0, padx=10)

today_card = tk.Label(
    summary_frame,
    text="Today\n₹0",
    font=("Arial", 14, "bold"),
    bg="#2196F3",
    fg="white",
    width=15,
    height=2
)
today_card.grid(row=0, column=1, padx=10)

month_card = tk.Label(
    summary_frame,
    text="This Month\n₹0",
    font=("Arial", 14, "bold"),
    bg="#FF9800",
    fg="white",
    width=15,
    height=2
)
month_card.grid(row=0, column=2, padx=10)

# ---------- ADD EXPENSE FRAME ----------

input_frame = tk.LabelFrame(root, text="Add Expense")
input_frame.pack(pady=10, padx=20, fill="x")

tk.Label(input_frame, text="Amount").grid(row=0, column=0, padx=10, pady=10)

entry_amount = tk.Entry(input_frame, width=15)
entry_amount.grid(row=0, column=1, padx=10)

tk.Label(input_frame, text="Category").grid(row=0, column=2, padx=10)

entry_category = ttk.Combobox(
    input_frame,
    values=category_list,
    width=15
)

entry_category.grid(row=0, column=3)
entry_category.set("Food")

tk.Label(input_frame, text="Description").grid(row=0, column=4, padx=10)

entry_desc = tk.Entry(input_frame, width=15)
entry_desc.grid(row=0, column=5, padx=10)

tk.Label(input_frame, text="Date").grid(row=0, column=6, padx=10)

entry_date = DateEntry(
    input_frame,
    width=12,
    date_pattern="yyyy-mm-dd"
)

entry_date.grid(row=0, column=7, padx=10)

tk.Button(
    input_frame,
    text="Add Expense",
    width=12,
    bg="#4CAF50",
    fg="white",
    command=add_expense
)


# ---------- SEARCH FRAME ----------

search_frame = tk.LabelFrame(root, text="Search / Filter")
search_frame.pack(pady=10, padx=20, fill="x")

tk.Label(search_frame, text="Category").grid(row=0, column=0, padx=10, pady=5)

search_category = ttk.Combobox(
    search_frame,
    values=category_list,
    width=15
)

search_category.grid(row=0, column=1, padx=10)

tk.Button(search_frame, text="Search", width=10,
          command=search_expense).grid(row=0, column=2, padx=10)

tk.Button(search_frame, text="Show All", width=10,
          command=view_expenses).grid(row=0, column=3, padx=10)


# ---------- ACTION BUTTONS ----------

button_frame = tk.LabelFrame(root, text="Actions")
button_frame.pack(pady=10, padx=20, fill="x")

tk.Button(
    input_frame,
    text="Add Expense",
    width=12,
    bg="#4CAF50",
    fg="white",
    command=add_expense
).grid(row=0, column=8, padx=10)

tk.Button(button_frame, text="Update",
          width=12,
          bg="#FF9800",
          fg="white",
          command=update_expense).grid(row=0, column=0, padx=10)

tk.Button(button_frame, text="Delete",
          width=12,
          bg="#F44336",
          fg="white",
          command=delete_expense).grid(row=0, column=1, padx=10)

tk.Button(button_frame, text="Export Excel",
          width=12,
          bg="#9C27B0",
          fg="white",
          command=export_excel).grid(row=0, column=2, padx=10)

tk.Button(button_frame, text="Refresh",
          width=12,
          bg="#607D8B",
          fg="white",
          command=refresh_table).grid(row=0, column=3, padx=10)

tk.Button(button_frame, text="Dashboard",
          width=12,
          bg="#2196F3",
          fg="white",
          command=show_dashboard).grid(row=0, column=4, padx=10)

tk.Button(button_frame, text="Clear",
          width=12,
          bg="#424242",
          fg="white",
          command=clear_fields).grid(row=0, column=5, padx=10)

# ---------- STATUS BAR ----------

status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 10),
    anchor="w",
    fg="green"
)

status_label.pack(fill="x", padx=10, pady=5)

# ---------- TOTAL EXPENSE LABEL ----------

total_label = tk.Label(
    root,
    text="Total Expenses: ₹0",
    font=("Arial", 14, "bold"),
    fg="green"
)

total_label.pack(pady=5)

summary_label = tk.Label(root, text="", font=("Arial",11))
summary_label.pack()

# ---------- TABLE FRAME ----------

table_frame = tk.Frame(root)
table_frame.pack(pady=20, padx=20, fill="both", expand=True)

columns = ("ID", "Amount", "Category", "Date", "Description")

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for col in columns:
    tree.heading(
        col,
        text=col,
        anchor="center",
        command=lambda _col=col: sort_column(tree, _col, False)
    )
    
tree.column("ID", width=60, anchor="center")
tree.column("Amount", width=120, anchor="center")
tree.column("Category", width=150, anchor="center")
tree.column("Date", width=120, anchor="center")
tree.column("Description", width=300, anchor="w")

tree.tag_configure("oddrow", background="white")
tree.tag_configure("evenrow", background="#f2f2f2")

tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

tree.configure(yscrollcommand=scrollbar.set)
scrollbar.configure(command=tree.yview)

tree.bind("<ButtonRelease-1>", select_record)


view_expenses()


root.mainloop()