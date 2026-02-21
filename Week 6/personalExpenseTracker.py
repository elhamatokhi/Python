# Exercise 3: Personal Expense Tracker
from datetime import datetime

# 1. Initialize Data Structures
expense_records = []       # list of (category, amount, date)
category_totals = {}       # sum spending by category
unique_categories = set()  # distinct categories

# 2. Collect Expense Data (5–7 expenses)
NUM_EXPENSES = 2
for i in range(1, NUM_EXPENSES + 1):
    while True:
        category = input(f"Enter expense {i} category: ").strip()
        if category:
            break
        print("  Category cannot be empty. Try again.")
    while True:
        amount_str = input(f"Enter expense {i} amount: ").strip()
        if not amount_str:
            print("  Amount cannot be empty. Try again.")
            continue
        try:
            amount = float(amount_str)
            if amount >= 0:
                break
            print("  Amount must be >= 0. Try again.")
        except ValueError:
            print("  Enter a valid number.")
    while True:
        date = input(f"Enter expense {i} date (YYYY-MM-DD): ").strip()
        if not date:
            print("  Date cannot be empty. Try again.")
            continue
        try:
            datetime.strptime(date, "%Y-%m-%d")
            break
        except ValueError:
            print("  Invalid date. Use YYYY-MM-DD (e.g. 2026-02-21). Try again.")
    expense_records.append((category, amount, date))

# 3. Categorize and Sum Expenses
for category, amount, date in expense_records:
    unique_categories.add(category)
    category_totals[category] = category_totals.get(category, 0) + amount

# 4. Calculate Overall Statistics
all_amounts = [amount for category, amount, date in expense_records]
total_spending = sum(all_amounts)
average_expense = total_spending / len(all_amounts) if all_amounts else 0
highest_expense = max(all_amounts) if all_amounts else 0
lowest_expense = min(all_amounts) if all_amounts else 0
overall_stats = {
    "total_spending": total_spending,
    "average_expense": average_expense,
    "highest_expense": highest_expense,
    "lowest_expense": lowest_expense,
}


def get_amount(record):
    """Return the amount (index 1) from a record tuple (category, amount, date)."""
    return record[1]


highest_expense_record = max(expense_records, key=get_amount) if expense_records else None
lowest_expense_record = min(expense_records, key=get_amount) if expense_records else None

# 5. Generate Spending Report
print("\n=== OVERALL SPENDING SUMMARY ===")
print(f"Total Spending: ${overall_stats['total_spending']:.2f}")
print(f"Average Expense: ${overall_stats['average_expense']:.2f}")
if highest_expense_record:
    print(f"Highest Expense: ${highest_expense_record[1]:.2f} (Category: {highest_expense_record[0]}, Date: {highest_expense_record[2]})")
if lowest_expense_record:
    print(f"Lowest Expense: ${lowest_expense_record[1]:.2f} (Category: {lowest_expense_record[0]}, Date: {lowest_expense_record[2]})")

print("\n=== UNIQUE CATEGORIES SPENT ON ===")
print(unique_categories)
print(f"Total unique categories: {len(unique_categories)}")

print("\n=== SPENDING BY CATEGORY ===")
for category, total in category_totals.items():
    print(f"{category}: ${total:.2f}")
