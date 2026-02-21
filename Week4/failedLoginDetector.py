login_attempts = [
("Elyas", "success"),
("Ahmad", "failed"),
("Ahmad", "failed"),
("Hena", "success"),
("Ahmad", "failed"),
("Elyas", "failed")
]

failed_counts = {}
# count failed login attempts
for username, status in login_attempts:
    if status =='failed':
        # Increment the failure count for this user (start at 0 if the user isn't in the dictionary yet)
        failed_counts[username] = failed_counts.get(username,0) + 1

# Check for accounts that failed 3 or more times
for username in failed_counts:
    if failed_counts[username]>= 3:
        print("ALERT: User '" + username + "' has " + str(failed_counts[username]) + " failed login attempts")

print('Security check completed')