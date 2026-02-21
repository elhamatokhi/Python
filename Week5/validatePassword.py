"""
Password rule checkers; each function returns True if the rule passes, False otherwise.
"""
import random
import string

# (result key, display label) for validation results
RULE_DISPLAY = [
    ("min_length", "Minimum length (8+ chars)"),
    ("uppercase", "Contains uppercase"),
    ("lowercase", "Contains lowercase"),
    ("digit", "Contains digit"),
    ("special_char", "Contains special character"),
]

# Random messages when password is weak (encouragement + hints)
WEAK_PASSWORD_MESSAGES = [
    "You can do it! Try adding more variety to your password.",
    "Tip: Mix uppercase, lowercase, numbers, and symbols like !@#$%^&*",
    "Strong passwords are at least 8 characters with mixed character types.",
    "Hint: Avoid common words—try a phrase with numbers and symbols.",
    "Keep going! A strong password helps keep your accounts secure.",
]


def check_min_length(password, min_len=8):
    # Return True if password has at least min_len characters.
    return len(password) >= min_len

def has_uppercase(password):
    #Return True if password contains at least one uppercase letter.
    return any(c in string.ascii_uppercase for c in password)


def has_lowercase(password):
    #Return True if password contains at least one lowercase letter.
    return any(c in string.ascii_lowercase for c in password)


def has_digit(password):
    # Return True if password contains at least one digit.
    return any(c in string.digits for c in password)


def has_special_char(password):
    # Return True if password contains at least one special character.
    return any(c in string.punctuation for c in password)


def validate_password(password):
    """
    Run all five validation checks and return a dictionary with each result
    and an overall is_valid (True only if all checks pass).
    """
    results = {
        "min_length": check_min_length(password),
        "uppercase": has_uppercase(password),
        "lowercase": has_lowercase(password),
        "digit": has_digit(password),
        "special_char": has_special_char(password),
    }
    results["is_valid"] = all(results.values()) # Returns true only if all requirements are true
    return results


def main():
    """Main program: banner, requirements, input, validation, and clear feedback."""
    print("=" * 50)
    print("PASSWORD STRENGTH VALIDATOR")
    print("=" * 50)
    print("\nPassword Requirements:")
    print("  • Minimum 8 characters")
    print("  • At least one uppercase letter")
    print("  • At least one lowercase letter")
    print("  • At least one digit")
    print("  • At least one special character (!@#$%^&* etc.)")
    print()

    password = input("Enter password to validate: ")
    results = validate_password(password)

    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)
    for key, label in RULE_DISPLAY:
        symbol = "✓" if results[key] else "✗"
        print(f"{symbol} {label}: {results[key]}")
    print("\n" + "=" * 50)
    if results["is_valid"]:
        print("✓ PASSWORD IS STRONG!")
    else:
        print("✗ PASSWORD IS WEAK - Please address failed requirements")
        print(f"  → {random.choice(WEAK_PASSWORD_MESSAGES)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
