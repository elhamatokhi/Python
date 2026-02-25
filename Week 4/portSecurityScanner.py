# Exercise 2: Port Security Scanner
# Identifies open risky ports on network devices.

devices = [
    ("192.168.1.20", [22, 80, 443]),
    ("192.168.2.20", [21, 22, 80]),
    ("192.168.2.20", [23, 80, 3389])
]

# Define a list of riky ports
risky_ports = [21, 23, 3389]
print("Scanning network devices...")

risk_count = 0
for ip, open_ports in devices:
    for port in open_ports:
        if port in risky_ports:
            print(f"WARNING: {ip} has risky port {port} open")
            risk_count += 1

print(f"Scan complete: {risk_count} security risks found")

