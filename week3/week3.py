# Lab 3 Exercise 1: Grade calculator
score = int((input("Enter your score: ")))

if(score >= 90 and score <= 100):
    grade = "A"
elif(score <=89 and score >= 80):
    grade = "B"
elif(score <= 79 and score >= 70):
    grade = "C"
elif(score <= 69 and score >= 60):
    grade = "D"
elif(score < 60):
    grade = "F"

print(f"Your grade: $ {grade}")

# Bonus: print encouragement for top grades
if grade == "A":
    print("Excellent work!")