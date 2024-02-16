import pandas as pd
import matplotlib.pyplot as plt

# Define the data
data = {
    'Score': [77, 81, 76, 74, 82, 72, 78, 74, 81, 74, 76, 81, 81, 77],
    'Days': [130, 154, 155, 168, 174, 175, 176, 186, 192, 200, 201, 209, 210, 238]
}

# Create a DataFrame from the data
df = pd.DataFrame(data)

# Plot the graph
plt.figure(figsize=(10, 6))
plt.plot(df['Days'], df['Score'], marker='o', linestyle='-')
plt.title('Score vs. Days')
plt.xlabel('Days')
plt.ylabel('Score')
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()
