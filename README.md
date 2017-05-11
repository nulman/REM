# REM - Resonable Experiments Manager
The Graph Generation System was designed to provide an interface for graph generation based on experiment data, using a client-server web interface.
Using this system, the user can connect to a website, select a specific data file, graph model and parameters, and plot a graph in the browser.
The graphs are generated using the [Bokeh](http://bokeh.pydata.org/en/latest/) library in python and are interactive - allowing zoom pan and save operations.
The system also allows to save/load/delete presets plots for different data files, as well as an option to define your own plugin.

# Features
An interface for graph generation from given data file.

- Interactive **file explorer** for easier experiment selection
- **Load preset**: allows the user to load a preset per data file, selecting a preset from a list and generating a graph from it in a single click.
- **Create preset**: allows the user to create a new graph preset from available graph models (line, step, heatmap etc..).
- **Save preset**: allows the user to save the selected parameters as a preset for other users to use.
- **Plugin system**:  allow the user to define their own graph model by writing their own plugin in python.
- **Select-by-value**: allows the user to define fields as "filter by value", which upon selection will display an additional input field to select by value. Select-by-value Fields can define a single or multiple selections.
- **Export**: Generated graph's data is also saved as a JSON (under the "exports" sub-directory) and the plot can be saved as an image (PNG) upon request.
- **Zoom/Pan**: Generated graphs are interactive in the browser, allowing zoom and pan.
- **Portability**: Database files (SQLite) holds the models and presets, and can be moved between machines to retain models/presets information.

# Documentation
More information and the project documentation can be found in the repository Wiki.

# Quick Install Guide
Currently, **REM** supports only Ubuntu Server.

Install the required packages.
```
sudo apt-get install git python python-dev python-pip
```

Pull the code from the repository.
```
git checkout git@github.com:nulman/REM.git
```

Install the requirements.
```
cd REM
pip install -r REQUIREMENTS
```

#  Quick Start

In the base folder of the code, run the following:
```
cd server
python server.py
```
