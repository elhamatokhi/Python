# Exercise 2: Student Grade Analyzer

# 1. Initialize Data Structures
# Dictionary: keys = student names (string), values = lists of grades (integers or floats)
student_grades = {}


# 2. Function to Add Student Grades
def add_student_grades(grades_db):
    """Prompt for a student's name and multiple grades."""
    name = input("Enter student name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    grades_input = input("Enter grades separated by spaces (e.g. 85 92 78): ").strip()
    if not grades_input:
        print("No grades entered.")
        return

    try:
        new_grades = [float(g) for g in grades_input.split()]
    except ValueError:
        print("Invalid input. Please enter numbers only, separated by spaces.")
        return

    if name in grades_db:
        grades_db[name].extend(new_grades)
        print(f"Added {len(new_grades)} grade(s) to {name}. Total grades: {len(grades_db[name])}")
    else:
        grades_db[name] = new_grades
        print(f"Added new student '{name}' with {len(new_grades)} grade(s).")


# 3. Function to Calculate Statistics
def get_student_stats(grades_db, student_name):
    """Return average, highest, and lowest grade for a student. Handle not found / no grades."""
    if student_name not in grades_db:
        print(f"Student '{student_name}' not found.")
        return None

    grades = grades_db[student_name]
    if not grades:
        print(f"Student '{student_name}' has no grades recorded.")
        return None

    avg = sum(grades) / len(grades)
    highest = max(grades)
    lowest = min(grades)
    return {"average": avg, "highest": highest, "lowest": lowest}


# 4. Function to Generate Full Report
def generate_full_report(grades_db):
    """Print report for all students (name, grades, avg, high, low) and overall average."""
    if not grades_db:
        print("No students in the database.")
        return

    all_grades = []
    print("\n" + "=" * 50)
    print("FULL GRADE REPORT")
    print("=" * 50)

    for name, grades in grades_db.items():
        if not grades:
            print(f"\n{name}: No grades recorded.")
            continue
        all_grades.extend(grades)
        avg = sum(grades) / len(grades)
        highest = max(grades)
        lowest = min(grades)
        print(f"\n{name}:")
        print(f"  Grades: {grades}")
        print(f"  Average: {avg:.2f}  |  Highest: {highest}  |  Lowest: {lowest}")

    if all_grades:
        overall_avg = sum(all_grades) / len(all_grades)
        print("\n" + "-" * 50)
        print(f"Overall average (all students): {overall_avg:.2f}")
    print("=" * 50)


# 5. Main Program Loop
def main():
    while True:
        print("\nStudent Grade Analyzer Menu:")
        print("1. Add grades for a student")
        print("2. View statistics for a student")
        print("3. Generate full report")
        print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_student_grades(student_grades)
        elif choice == "2":
            name = input("Enter student name: ").strip()
            if name:
                result = get_student_stats(student_grades, name)
                if result is not None:
                    print(
                        f"  Average: {result['average']:.2f}  |  "
                        f"Highest: {result['highest']}  |  Lowest: {result['lowest']}"
                    )
        elif choice == "3":
            generate_full_report(student_grades)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
