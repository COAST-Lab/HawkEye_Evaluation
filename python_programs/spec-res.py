import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Define the spectral bands for each satellite sensor in micrometers (µm) for better comparison
seahawk_hawkeye_bands = [
    (0.400, 0.410), (0.412, 0.422), (0.443, 0.453), (0.490, 0.500),
    (0.510, 0.520), (0.555, 0.565), (0.620, 0.630), (0.665, 0.675),
    (0.681, 0.691), (0.709, 0.719), (0.753, 0.763), (0.776, 0.786),
    (0.865, 0.875)
]

aqua_modis_bands = [
    (0.412, 0.422), (0.443, 0.453), (0.488, 0.498), (0.531, 0.541),
    (0.547, 0.557), (0.555, 0.565), (0.667, 0.677), (0.678, 0.688),
    (0.748, 0.758), (0.869, 0.879)
]

sentinel_3A_B_OLCI_bands = [
    (0.400, 0.410), (0.412, 0.422), (0.443, 0.453), (0.490, 0.500),
    (0.510, 0.520), (0.560, 0.570), (0.620, 0.630), (0.665, 0.675),
    (0.681, 0.691), (0.709, 0.719), (0.754, 0.764), (0.779, 0.789),
    (0.865, 0.875)
]

# Plot the spectral bands
fig, ax = plt.subplots(figsize=(12, 6))

# Define a function to add spectral bands as rectangles
def add_spectral_bands(ax, bands, y_position, color, label):
    for band in bands:
        rect = patches.Rectangle((band[0], y_position - 0.1), band[1] - band[0], 0.2, linewidth=1, edgecolor=color, facecolor=color, label=label)
        ax.add_patch(rect)
        label = None  # To ensure the label is only added once to the legend

# Add spectral bands to the plot
add_spectral_bands(ax, seahawk_hawkeye_bands, 1, 'blue', 'SeaHawk-HawkEye')
add_spectral_bands(ax, aqua_modis_bands, 2, 'green', 'Aqua-MODIS')
add_spectral_bands(ax, sentinel_3A_B_OLCI_bands, 3, 'red', 'Sentinel-3A/B OLCI')

# Customize the plot
ax.set_yticks([1, 2, 3])
ax.set_yticklabels(['SeaHawk-HawkEye', 'Aqua-MODIS', 'Sentinel-3A/B OLCI'])
ax.set_xlabel('Wavelength (µm)')
ax.set_title('Spectral Wavelengths and Bandwidths for SeaHawk-HawkEye, Aqua-MODIS, and Sentinel-3A/B OLCI')
ax.legend(loc='upper right')
ax.grid(True)

plt.show()
