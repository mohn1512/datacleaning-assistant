import pandas as pd
import numpy as np
import random

# Set seed for reproducibility
np.random.seed(42)

# Generate synthetic data
data = {
    "CustomerID": [f"CUST{1000+i}" for i in range(100)],
    "Name": [random.choice(["Alice", "Bob", "Charlie", "alice", "BOB", None]) for _ in range(100)],
    "Age": [random.choice([25, 35, np.nan, 45, 1000, "unknown"]) for _ in range(100)],
    "Email": [f"user{i}@domain.com" if i % 10 != 0 else None for i in range(100)],
    "SignupDate": [random.choice(["2021-01-01", "01/02/2021", None, "2021/03/03"]) for _ in range(100)],
    "Country": [random.choice(["USA", "India", "usa", "IN", "U.S.", None]) for _ in range(100)],
    "PurchaseAmount": [round(random.uniform(10, 1000), 2) if i % 9 != 0 else None for i in range(100)],
}

# Add duplicate rows
df = pd.DataFrame(data)
df = pd.concat([df, df.iloc[0:5]], ignore_index=True)

# Save to CSV
df.to_csv("messy_data.csv", index=False)
print("✅ Messy dataset saved as 'messy_data.csv'")
