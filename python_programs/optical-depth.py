import matplotlib.pyplot as plt

# Data for first optical depth
sensors = ['MODIS', 'HawkEye', 'S3A-OLCI', 'S3B-OLCI']
kd_values = [0.187, 0.0252, 0.163, 0.324]
first_optical_depth = [1/kd for kd in kd_values]  # Calculating first optical depth

# Creating the bar graph
plt.figure(figsize=(5, 5))
plt.bar(sensors, first_optical_depth, color=['blue', 'green', 'red', 'purple'])
plt.xlabel('Sensor')
plt.ylabel('First Optical Depth (m)')
plt.title('First Optical Depth for Each Sensor')
plt.ylim(0, max(first_optical_depth) + 5)  # Adjusting y-axis limit for better visibility

# Displaying the graph
plt.show()
