import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np

def create_colorbar(orientation='horizontal', title_size=12):  # Add title_size parameter with default value
    # Set figure size based on orientation
    fig_size = (12, 0.5) if orientation == 'horizontal' else (0.5, 12)
    
    # Create a figure and a single subplot with a facecolor of #FAFAFA
    fig, ax = plt.subplots(figsize=fig_size, facecolor='#FAFAFA')

    # Set the colormap
    cmap = plt.cm.Greens

    # Define the bounds for the normalization using a logarithmic scale
    norm = Normalize(vmin=np.log10(0.1), vmax=np.log10(5.5))

    # Create a ScalarMappable and initialize a data array with the scalar data to map
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    # Create the colorbar with logarithmic ticks
    cbar = plt.colorbar(sm, cax=ax, orientation=orientation, 
                        aspect=10)  # aspect makes the colorbar thinner
    cbar.set_ticks(np.log10([0.1, 0.2, 0.5, 1.0, 2.0, 5.0]))
    cbar.set_ticklabels(['0.1', '0.2', '0.5', '1.0', '2.0', '5.0'])

    # Set the colorbar label with adjustments for horizontal and vertical orientation and apply the title_size
    if orientation == 'horizontal':
        cbar.set_label('Chlorophyll (µg/L)', rotation=0, labelpad=10, fontsize=title_size)
        cbar.ax.xaxis.set_label_position('bottom')
    else:
        cbar.set_label('Chlorophyll (µg/L)', rotation=90, labelpad=10, fontsize=title_size)

    # Set the tick labels size
    cbar.ax.tick_params(labelsize=12)

    # Set the background color of the colorbar to #FAFAFA
    cbar.ax.set_facecolor('#FAFAFA')

    # Save the colorbar to a file with a #FAFAFA background
    colorbar_path = f'/Users/mitchtork/HawkEye_Evaluation/python/helper_data/colorbar_{orientation}.png'
    plt.savefig(colorbar_path, dpi=300, bbox_inches='tight', facecolor='#FAFAFA')

    # Close the plot to avoid displaying it in the notebook output
    plt.close()

    return colorbar_path

# Usage with adjustable title size
horizontal_colorbar_path = create_colorbar('horizontal', title_size=16)
vertical_colorbar_path = create_colorbar('vertical', title_size=16)
