# Exercise 2: Limited Login Attempts
correct_pin = "3458"
attempts = 0
max_attempts = 3
login_successful = False

while attempts < max_attempts:
    print(f"Attempt {attempts + 1} of {max_attempts}")
    entered_pin = input("Enter your PIN: ")

    if entered_pin == correct_pin:
        print("PIN accepted! Welcome.")
        login_successful = True
        break # exit the loop if PIN is correct
    else: 
        print("Incorrect PIN.")
        attempts += 1

if not login_successful:
    print("Too many incorrect attempts,. Account locked.")
