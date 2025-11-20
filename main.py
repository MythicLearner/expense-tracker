from db import init_db, get_connection, DB_PATH
from datetime import datetime

CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Shopping",
    "Entertainment",
    "Health",
    "Other",
]

def choose_category():
    while True:
        print("\nChoose a category:")
        for i, cat in enumerate(CATEGORIES, start=1):
            print(f"[{i}] {cat}")
        choice = input("Enter number: ").strip()

        try:
            idx = int(choice)
            if 1 <= idx <= len(CATEGORIES):
                return CATEGORIES[idx - 1]
            else:
                print("Invalid choice. Please pick one of the numbers shown.")
        except ValueError:
            print("Please enter a number.")


def add_expense():

    date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    conn = get_connection()
    cur = conn.cursor()
    while True:
        amount = input ("Enter amount: ").strip()

        try:
            amount = float(amount)
            if amount <= 0:
                print("Amount must be greater than zero.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")
        
    
    category = choose_category()
    note = input ("Enter note (optional): ").strip()

    if not amount or not category:
        print("Amount and category are required.")
        return
    
    cur.execute (
        "INSERT INTO expenses (date, amount, category, note) VALUES (?, ?, ?, ?)",
        (date, amount, category, note if note else None)
    )
    conn.commit()
    conn.close()

    print ("Expense added successfully")

def view_expenses(limit = None):

    conn = get_connection()
    cur = conn.cursor()

    if limit :

        cur.execute (
            "SELECT id, date, amount, category, COALESCE (note, '') FROM expenses ORDER BY date DESC LIMIT ?",
            (limit,)
        )
    else:

        cur.execute (
            "SELECT id, date, amount, category, COALESCE (note, '') FROM expenses ORDER BY date DESC"
        )
    rows = cur.fetchall()
    conn.close()

    print("\nID | Date                | Amount | Category | Note")
    print("-" * 65)
    for rid , Date, Amount, Category, Note in rows:
        print(f"{rid:>2} | {Date:<19} | {Amount:>8.2f} | {Category:<10} | {Note}")
    print()

def totals_by_category():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute (
        "SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC"
    )
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("\nNo expenses found.\n")
        return
    
    print("\nCategory          | Total Amount")
    
    print("-" * 30)
    for Category, Total in rows:
        print(f"{Category:<15} | {Total:>8.2f}")
    print()

def edit_expense():

    print("\nRecent expenses:")
    view_expenses(limit=10)

    id_input = input("Enter the ID of the expense to edit (or blank to cancel): ").strip()
    if id_input == "":
        print("Edit cancelled.")
        return

    try:
        expense_id = int(id_input)
    except ValueError:
        print("ID must be a number.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, date, amount, category, COALESCE(note, '') FROM expenses WHERE id = ?", (expense_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        print("No expense found with that ID.")
        return

    _, date, amount, category, note = row
    print(f"\nCurrent values for ID {expense_id}:")
    print(f"Date:     {date}")
    print(f"Amount:   {amount}")
    print(f"Category: {category}")
    print(f"Note:     {note}")

    # edit amount
    while True:
        new_amount_input = input(f"New amount (leave blank to keep {amount}): ").strip()
        if new_amount_input == "":
            new_amount = amount
            break
        try:
            new_amount = float(new_amount_input)
            if new_amount <= 0:
                print("Amount must be positive.")
                continue
            break
        except ValueError:
            print("Invalid amount. Please enter a number.")

    # edit category (optional: 0 = keep current)
    print("\nEdit category (0 to keep current):")
    while True:
        print(f"Current category: {category}")
        for i, cat in enumerate(CATEGORIES, start=1):
            print(f"[{i}] {cat}")
        cat_choice = input("Enter number (or 0): ").strip()

        try:
            idx = int(cat_choice)
            if idx == 0:
                new_category = category
                break
            elif 1 <= idx <= len(CATEGORIES):
                new_category =  CATEGORIES[idx - 1]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

    # edit note
    new_note = input(f"New note (leave blank to keep current): ").strip()
    if new_note == "":
        new_note = note

    # update database
    cur.execute(
        "UPDATE expenses SET amount = ?, category = ?, note = ? WHERE id = ?",
        (new_amount, new_category, new_note, expense_id),
    )
    conn.commit()
    conn.close()

    print("Expense updated.")

def delete_expense():
    print("\nRecent expenses:")
    view_expenses(limit=10)

    id_input = input("Enter the ID of the expense to delete (or blank to cancel): ").strip()
    if id_input == "":
        print("Delete cancelled.")
        return

    try:
        expense_id = int(id_input)
    except ValueError:
        print("ID must be a number.")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        print("No expense found with that ID.")
        return

    confirm = input(f"Are you sure you want to delete expense ID {expense_id}? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Delete cancelled.")
        conn.close()
        return

    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    print("Expense deleted.")

def main():
    while True:
        print ("Expense Tracker")
        print ("[1] Add Expense")
        print ("[2] View Last 10 Expenses")
        print ("[3] View All Expenses")
        print ("[4] Totals by Category")
        print ("[5] Edit an Expense")
        print ("[6] Delete an Expense")
        print ("[0] Exit")    
        choice = input ("Choose an option: ").strip()
        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses(limit=10)
        elif choice == "3":
            view_expenses()
        elif choice == "4":
            totals_by_category()
        elif choice == "5":
            edit_expense()
        elif choice == "6":
            delete_expense()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.\n")


    
    init_db()
    conn = get_connection()

    cur = conn.cursor()
    conn.commit()

    conn.close()

if __name__ == "__main__":
    main()
