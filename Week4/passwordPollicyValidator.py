# Exercise 3: Password Policy Validator
# Checks compliance with security policies.

# Create a list of user passwords mostly used in Germany
passwords = [
    'pass123',
    "123456",
    "123456789",
    "hello123", 
    "coffee", 
     "cup", 
    "password",
    "lol123",
    "Pass123",
    "weak",
    "NOLOWER123"
    "SecurePassword1",
    "MyP@ssw0rd",
]

print('Validating passwords...')

# Initialize compliant and non-compliant passwords counters
compliant = 0
non_compliant = 0

for pwd in passwords:
    too_short = len(pwd) < 8
    has_upper = False
    has_lower = False
    has_digit = False

    for char in pwd:
        if char >= "A" and char <= "Z":
            has_upper = True
        if char >= "a" and char <= "z":
            has_lower = True
        if char >= "0" and char <= "9":
            has_digit = True

    reasons = []
    if too_short:
        reasons.append("Too short")
    if not has_upper:
        reasons.append("No uppercase")
    if not has_lower:
        reasons.append("No lowercase letters")
    if not has_digit:
        reasons.append("No digits")

# Compliant passwords

    if len(reasons) == 0:
        print(f"PASS: '{pwd}' - Meets all requirements")
        compliant += 1
    else:
        print(f"FAIL: '{pwd}' - {', '.join(reasons)}")
        non_compliant += 1


print("Summary: " + str(compliant) + " compliant, " + str(non_compliant) + " non-compliant")
