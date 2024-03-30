import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Function to parse the timestamp
def parse_timestamp(ts_str):
    try:
        return datetime.strptime(str(ts_str), '%Y%m%d.%H%M%S')
    except ValueError:
        # Handle the case where ts_str cannot be converted
        return pd.NaT

# Adjust the file_path as necessary
file_path = "C:/Users/TEST_BED_COMPUTER/Desktop/EDGE_Test_kit/Yokogawa_20240312.143837/ch1.csv"

# Read the CSV file, adjust sep according to your file's format
data = pd.read_csv(file_path, sep=',', header=0)  # Example: using comma-separated

# Convert 'Timestamp' column to datetime format
data['Timestamp'] = data['Timestamp'].apply(parse_timestamp)

# Filter out rows where the timestamp could not be parsed
data = data.dropna(subset=['Timestamp'])

# Prepare the plot
plt.figure(figsize=(15, 10))  # Adjust size for better visibility

# Plot each parameter against the timestamp
for column in data.columns:
    if column != 'Timestamp':
        plt.plot(data['Timestamp'], data[column], label=column)

plt.xlabel('Timestamp')
plt.ylabel('Values')
plt.title('Parameters over Time')

# Format the x-axis to show hours:minutes and set locator to every 5 minutes
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))  # Adjust the interval as needed
plt.gcf().autofmt_xdate()  # Improve formatting of the x-axis labels

plt.legend()
plt.tight_layout()
plt.show()
