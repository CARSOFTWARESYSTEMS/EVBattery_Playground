# EV.ENGINEER | carsoftwaresystems@gmail.com | CAR SOFTWARE SYSTEMS (.com)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Read the CSV file into a DataFrame
data_file = '/Users/ananth/Developer/ev.engineer/python/ev_battery/temperature/battery_data.csv'
df = pd.read_csv(data_file)

# Display the first few rows to check the data
print("Data Preview:")
print(df.head())
df = pd.read_csv(data_file, parse_dates=['Timestamp'])
print(df.to_timestamp)

# Calculate statistics for the Temperature column
average_temp = df['Temperature'].mean()
max_temp = df['Temperature'].max()
min_temp = df['Temperature'].min()

print(f"Average Temperature: {average_temp:.2f}°C")
print(f"Maximum Temperature: {max_temp:.2f}°C")
print(f"Minimum Temperature: {min_temp:.2f}°C")

plt.figure(figsize=(12, 6))
plt.plot(df['Timestamp'], df['Temperature'], marker='o', linestyle='-', color='blue')
plt.title('Battery Temperature Trend')
plt.xlabel('Timestamp')
plt.ylabel('Temperature (°C)')
plt.grid(True)
plt.xticks(rotation=45)  # Rotate the timestamps for better readability
plt.tight_layout()
plt.show()


overheat_threshold = 60  # Temperature threshold in °C

# Find rows where temperature exceeds the threshold
overheat_events = df[df['Temperature'] > overheat_threshold]

if not overheat_events.empty:
    print("Overheating Alert! The following entries exceed the threshold:")
    print(overheat_events[['Timestamp', 'Temperature']])
else:
    print("No overheating events detected.")


