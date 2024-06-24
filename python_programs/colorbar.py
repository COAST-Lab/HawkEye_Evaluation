import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
from matplotlib.ticker import ScalarFormatter
import numpy as np
import cmocean
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

variable_properties = {
    'do': {
        'cmap': cmocean.cm.deep,
        'norm': Normalize(vmin=7.36524, vmax=7.45626),
        'label_text': 'Dissolved Oxygen (mg/L)'
    },
    'turbidity': {
        'cmap': cmocean.cm.turbid,
        'norm': Normalize(vmin=0.0, vmax=10.986),
        'label_text': 'Turbidity (NTU)'
    },
    'density': {
        'cmap': cmocean.cm.dense,
        'norm': Normalize(vmin=1024.6705, vmax=1024.9357),
        'label_text': 'Density (kg/m³)'
    },
    'salinity': {
        'cmap': cmocean.cm.haline,
        'norm': Normalize(vmin=34.9221, vmax=35.0453),
        'label_text': 'Salinity (PSU)'
    },
    'temp': {
        'cmap': cmocean.cm.thermal,
        'norm': Normalize(vmin=19.548, vmax=20.2196),
        'label_text': 'Temperature (°C)'
    },
    'wind': {
        'cmap': plt.cm.viridis,
        'norm': Normalize(vmin=0.06, vmax=5.63),
        'label_text': 'Wind Speed (m/s)'
    },
    'kd490': {
        'cmap': plt.cm.viridis,
        'norm': Normalize(vmin=0.15639999604900368, vmax=1.0691999729897361),
        'label_text': 'Kd490 (m−1)'
    },
    'chlor_a': {
        'cmap': cmocean.cm.algae,
        'norm': LogNorm(vmin=0.001, vmax=2.02),
        'label_text': 'Chlorophyll a (µg/L)'
    }
}

def create_colorbar(variable, orientation='horizontal', title_size=30, tick_size=40):
    props = variable_properties[variable]
    fig_size = (10, 0.5) if orientation == 'horizontal' else (0.5, 10)
    fig, ax = plt.subplots(figsize=fig_size)
    
    cmap = props['cmap']
    norm = props['norm']
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, cax=ax, orientation=orientation, aspect=10)
    cbar.ax.tick_params(labelsize=tick_size)

    # Set the tick formatter for density to avoid scientific notation
    if variable == 'density':
        if orientation == 'horizontal':
            cbar.ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        else:
            cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))

    label_text = props['label_text']
    if orientation == 'horizontal':
        cbar.set_label(label_text, rotation=0, labelpad=5, fontsize=title_size)
        cbar.ax.xaxis.set_label_position('bottom')
    else:
        cbar.set_label(label_text, rotation=90, labelpad=10, fontsize=title_size)
    
    colorbar_path = os.path.join(SAVE_DIR, f'{variable}_{orientation}.png')
    plt.savefig(colorbar_path, dpi=500, bbox_inches='tight')
    print("Saving colorbar at:", colorbar_path)
    plt.close()

    return colorbar_path

# Example Usage
horizontal_colorbar_path_log = create_colorbar('chlor_a', 'horizontal', title_size=16, tick_size=16)
vertical_colorbar_path_normal = create_colorbar('chlor_a', 'vertical', title_size=22, tick_size=20)
