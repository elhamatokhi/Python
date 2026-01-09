'''Business profit calculator profit and margin percentage from revenue and cost data'''

# Get revenue from user
revenue =  float(input("Enter total revenue`; $"))

# Get costs from user
costs = float(input("Enter total consts: $"))

# Calculate profit
profit = revenue - costs

# Caclulate profit margin percentage
margin = (profit / revenue) * 100

# Display results

print("\n--- Financial Summary ---")
print(f"Revenue: ${revenue:}")
print(f"Costs: ${costs}")
print(f"Profit: ${profit}")
print(f"Profit Margin: ${margin}")