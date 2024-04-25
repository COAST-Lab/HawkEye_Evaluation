import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LogNorm
import numpy as np
import cmocean
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(SCRIPT_DIR, 'local_processing_resources')
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

variable_properties = {
    'ox_sat': {
        'cmap': cmocean.cm.deep,  # Colormap for oxygen saturation
        'norm': Normalize(vmin=7.36524, vmax=7.45626),  # Normalization range for oxygen saturation
        'tick_values': np.linspace(7.36524, 7.45626, 7),  # Tick values for the colorbar
        'label_text': 'Oxygen Saturation (%)'  # Label for the colorbar
    },
    'turbidity': {
        'cmap': cmocean.cm.turbid,  # Colormap for turbidity
        'norm': Normalize(vmin=0.0, vmax=10.986),  # Normalization range for turbidity
        'tick_values': np.linspace(0.0, 10.986, 7),  # Tick values for the colorbar
        'label_text': 'Turbidity (NTU)'  # Label for the colorbar
    },
    'density': {
        'cmap': cmocean.cm.dense,  # Colormap for density
        'norm': Normalize(vmin=1024.6705, vmax=1024.9357),  # Normalization range for density
        'tick_values': np.linspace(1024.6705, 1024.9357, 7),  # Tick values for the colorbar
        'label_text': 'Density (kg/m³)'  # Label for the colorbar
    },
    'salinity': {
        'cmap': cmocean.cm.haline,  # Colormap for salinity
        'norm': Normalize(vmin=34.9221, vmax=35.0453),  # Normalization range for salinity
        'tick_values': np.linspace(34.9221, 35.0453, 7),  # Tick values for the colorbar
        'label_text': 'Salinity (PSU)'  # Label for the colorbar
    },
    'temp': {
        'cmap': cmocean.cm.thermal,  # Colormap for temperature
        'norm': Normalize(vmin=19.548, vmax=20.2196),  # Normalization range for temperature
        'tick_values': np.linspace(19.548, 20.2196, 7),  # Tick values for the colorbar
        'label_text': 'Temperature (°C)'  # Label for the colorbar
    },
    'wind': {
        'cmap': plt.cm.viridis,
        'norm': Normalize(vmin=0.02621171437203884, vmax=9.460841178894043),
        'tick_values': np.linspace(0.02621171437203884, 9.460841178894043, 7),
        'label_text': 'Wind Speed (m/s)'
    },
    'kd490': {
        'cmap':  plt.cm.viridis,
        'norm': Normalize(vmin=0.01, vmax=0.20),
        'tick_values': np.linspace(0.01, 0.20, 7),
        'label_text': 'Kd490 (m−1)'
    },
    'chlor_a': {
        'cmap': cmocean.cm.algae,
        'norm': LogNorm(vmin=0.1, vmax=5.5),
        'tick_values': np.logspace(np.log10(0.1), np.log10(5.5), num=7),
        'label_text': 'Chlorophyll a (µg/L)'
    }
}

def create_colorbar(variable, orientation='horizontal', title_size=12, use_log_scale=False):
    props = variable_properties[variable]
    fig_size = (10, 0.5) if orientation == 'horizontal' else (0.5, 12)
    fig, ax = plt.subplots(figsize=fig_size)
    
    cmap = props['cmap']
    norm = props['norm']
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, cax=ax, orientation=orientation, aspect=10)
    cbar.set_ticks(props['tick_values'])
    cbar.set_ticklabels(['{:.2f}'.format(tick) for tick in props['tick_values']])
    cbar.ax.tick_params(labelsize=title_size)

    label_text = props['label_text']
    if orientation == 'horizontal':
        cbar.set_label(label_text, rotation=0, labelpad=10, fontsize=title_size)
        cbar.ax.xaxis.set_label_position('bottom')
    else:
        cbar.set_label(label_text, rotation=90, labelpad=10, fontsize=title_size)
    
    colorbar_path = os.path.join(SAVE_DIR, f'{variable}_{orientation}.png')
    plt.savefig(colorbar_path, dpi=500, bbox_inches='tight')
    print("Saving colorbar at:", colorbar_path)
    plt.close()

    return colorbar_path

# Example Usage
horizontal_colorbar_path_log = create_colorbar('chlor_a', 'horizontal', title_size=16, use_log_scale=True)
vertical_colorbar_path_normal = create_colorbar('chlor_a', 'vertical', title_size=16, use_log_scale=True)