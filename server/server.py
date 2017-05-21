"""
@editor: Liran Funaro <funaro@cs.technion.ac.il>
@author: Alex Nulman <anulman@cs.haifa.ac.il>

this is teh main app, it takes no parameters, instead update config.py
"""

import os
import json
import logging

from flask import Flask, request, session, redirect,  abort, Response
from flask.helpers import send_from_directory

from config import config
import internals_db
import traceback

from data_source import DataSource
import directory_listing

from plugin_manager import PluginManager

app = Flask(__name__)
plugins = PluginManager(config["plugins_path"])
internals = internals_db.InternalsDB(config["internals_db"])

app.config.from_object(__name__)
app.config.update(config) # apply config file settings
data_root_dir = app.config.get('data_root_dir', os.path.dirname(os.path.abspath(__file__)))

app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.DEBUG)


@app.errorhandler(Exception)
def handle_invalid_usage(error):
    """ Handles exception of all the handlers """
    app.logger.exception(error)

    if isinstance(error, SyntaxError):
        message = "Malformed experiment file: " + str(error)
    else:
        message = str(error)

    app.logger.exception(error)
    message  = "%s\n\n%s" % (message, traceback.format_exc())
    return Response(message, 500)


@app.route('/',methods=['GET'])
def main_page():
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


########################################################################
# Directory Listing
########################################################################

@app.route('/listdir',methods=['POST'])
def list_dir():
    """ Generates subtrees for the file browser """
    requested_path_list = request.get_json(force=True)
    app.logger.debug("Requested path list: %s", requested_path_list)

    if requested_path_list:
        requested_path = os.path.join(*requested_path_list)
    else:
        requested_path = data_root_dir

    app.logger.debug("Requested path: %s", requested_path)

    res = directory_listing.get_subtree(requested_path)
    return Response(json.dumps({
        'json': list(res),
        'url': requested_path,
        'url_list': os.path.split(requested_path)
    }), mimetype='application/json')


########################################################################
# Data Fetching and Plotting
########################################################################

@app.route('/data/getcolumns',methods=['POST'])
def get_columns():
    '''
    initialized the experiment data object and parses the experiment file if required
    returns the column names in the experiment and the graph plugins
    '''
    requested_path = request.get_json(force=True)
    app.logger.debug("Requested path: %s", requested_path)

    data = DataSource(requested_path, config['export_path'])

    res = data.column_names
    return Response(json.dumps(res), mimetype='application/json')


@app.route('/data/getvals',methods=['POST'])
def get_distinct_values():
    """ Returns all the distinct values of a data column """
    request_data = request.get_json(force=True)
    data_file = request_data['data_file']
    parameters = request_data['parameters']

    data = DataSource(data_file, config['export_path'])
    ret = data.get_distinct_values(parameters)
    return Response(json.dumps(ret), mimetype='application/json')


@app.route('/data/plot',methods=['POST'])
def plot():
    request_data = request.get_json(force=True)
    data_file = request_data['data_file']
    graph_type = request_data['graph_type']
    parameters = request_data['parameters']

    data = DataSource(data_file, config['export_path'])
    if not data.column_names:
        raise Exception("No data in file.")

    js, div = plugins[graph_type].plot(data, **parameters)
    return Response(json.dumps({'div':div, 'js':js}),
                    mimetype='application/json')


########################################################################
# Plugins
########################################################################


@app.route('/plugin/list',methods=['GET', 'POST'])
def plugin_list():
    request_data = request.get_json(force=True)
    if isinstance(request_data, str) and request_data.lower() == "reload":
        plugins.reload_plugins()

    ret = plugins.plugins_images()
    return Response(json.dumps(ret), mimetype='application/json')


@app.route('/plugin/parameters',methods=['POST'])
def plugin_parameters():
    request_data = request.get_json(force=True)
    ret = plugins.get_plugin_parameters(request_data)
    return Response(json.dumps(ret), mimetype='application/json')


########################################################################
# Preset Handling
########################################################################


@app.route('/preset/load',methods=['POST'])
def load_preset():
    '''
    returns presets depending on the requested value:
    empty - will return all presets in the database
    data_file - will return presets that can apply to the selected experiment file
    '''
    res = {}
    data_file = request.get_json(force=True)
    frame = internals.get_frames()

    if not data_file: # Empty message return all presets
        for index, row in frame.iterrows():
            res[row['name']] = json.loads(row['json'])
    else:
        data = DataSource(data_file, config['export_path'])
        sieve = set(data.column_names)
        for index, row in frame.iterrows():
            i = 0
            items = row['items'].split(',')
            for item in items:
                if item in sieve:
                    i+=1
                else:
                    break
            if i == len(items):
                res[row['name']] = json.loads(row['json'])
    return Response(json.dumps(res), mimetype='application/json')

    
@app.route('/preset/save',methods=['POST'])
def save_preset():
    '''
    recieves a {'name':name, "preset": preset} dict
    where name is an arbitrary name for the preset (will overwrite presets with he same name)
    and preset is the the same as a graphplugin.getparameters
    example:
    {"name":"thing2","preset":{"Line":{"x_axis":"timestamp","y_axis":"performance","group_by":{"name":["vm-1","vm-2"]}}}}
    '''
    parameters = request.get_json(force=True)
    if type(parameters) != dict:
        raise Exception("Expecting a dict, got a "+type(parameters))

    items = []
    name = parameters['name']
    preset = parameters['preset']
    graph_type = preset['graph_type']
    parameters = preset['parameters']

    plugin_parameters = plugins.get_plugin_parameters(graph_type)
    for key, param in parameters.items():
        ditem = plugin_parameters[key]
        if ditem['filterByValue']: #turns values back into column names (such as vm-1 => name)
            items.append(param.keys()[0])
        elif type(param) == list:
            for sub_item in param:
                items.append(sub_item)
        else:
            items.append(param)

    internals.save_frame(name, preset, items)

    return Response(json.dumps(['Preset saved.']), mimetype='application/json')


@app.route('/preset/delete',methods=['POST'])
def delete_preset():
    '''
    takes a list of names and deletes the associated presets if any
    example:
    ["name1","name2"]
    '''
    presets = request.get_json(force=True)
    if type(presets) != list or len(presets) == 0:
        raise Exception("Expecting a non-empty list.")

    internals.delete_frames(*presets)

    return Response(json.dumps(['Preset deleted.']), mimetype='application/json')


################################################################
# Main
################################################################
if __name__ == '__main__':
    try:
        print "-I- starting server on port {}".format(app.config['port'])
        app.run(app.config['hostname'], port = app.config['port'], threaded=True)
    except KeyboardInterrupt:
        exit(0)
