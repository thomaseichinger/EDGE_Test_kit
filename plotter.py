import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
csv_file_path = "your_csv_file.csv"  # Change to the path of your CSV file
data = pd.read_csv(csv_file_path)

# Assuming the CSV has columns named 'X' and 'Y'
x = data['X']  # Replace 'X' with the actual column name for the X-axis
y = data['Y']  # Replace 'Y' with the actual column name for the Y-axis

# Plotting
plt.figure(figsize=(10, 6))  # Optional: Adjusts the figure size
plt.plot(x, y, marker='o', linestyle='-', color='b')  # You can customize the plot
plt.title('Plot from CSV Data')  # Add a title
plt.xlabel('X-axis Label')  # Customize X-axis label
plt.ylabel('Y-axis Label')  # Customize Y-axis label
plt.grid(True)  # Adds a grid
plt.show()
