// @author: Liran Funaro <funaro@cs.technion.ac.il>

// #############################################################################
// Directory Listing
// #############################################################################

//makes a request to the server to get the tree information with the given url
//if the request was successful, the success function is then called
function asyncListDir(path, onSuccess) {
  return $.ajax({
        url : "/listdir",

        type : "POST",
        async : true,

        contentType:'application/json',
        dataType : "json",
        data: JSON.stringify(path),

        success : onSuccess,
    });
}


// #############################################################################
// Data Fetching and Plotting
// #############################################################################


function asyncGetColumns(path, onSuccess, onError) {
    return $.ajax({
        url: "/data/getcolumns",

        type: "POST",
        async: true,

        contentType:'application/json',
        dataType : "json",

        data: JSON.stringify(path),

        success: onSuccess,
        error: onError,
      });
}


function asyncGetValues(data_file, parameters, onSuccess) {
    return $.ajax({
        url : "/data/getvals",

        type: "POST",
        aync : true,

        contentType:'application/json',
        dataType:'json',

        data: JSON.stringify({
          data_file: data_file,
          parameters: parameters,
        }),

        success :  onSuccess,
    });
}


//sends the selected parameters to the server to plot
function asyncPlot(data_file, graph_type, parameters, onSuccess, onError){
  //send to server to generate graph
  return $.ajax({
      url: "/data/plot",

      type: "POST",

      contentType:'application/json',
      dataType:'json',

      data: JSON.stringify({
        data_file: data_file,
        graph_type: graph_type,
        parameters: parameters,
      }),

      success: onSuccess,
      error: onError,
    });
}


// #############################################################################
// Plugins
// #############################################################################


function asyncListPlugin(do_reload, onSuccess) {
    return $.ajax({
      url: "/plugin/list",

      type: "POST",

      contentType:'application/json',
      dataType:'json',

      data: JSON.stringify(do_reload ? "reload" : ""),

      success: onSuccess,
    })
}


function asyncPluginParameters(plugin_name, onSuccess) {
    return $.ajax({
      url: "/plugin/parameters",

      type: "POST",

      contentType:'application/json',
      dataType:'json',

      data: JSON.stringify(plugin_name),

      success: onSuccess,
    })
}


// #############################################################################
// Preset Handling
// #############################################################################


//requests the preset list from the server - used to fill the 'load' section
function asyncLoadPresets(data_file, onSuccess) {
  return $.ajax({
        url : "/preset/load",

        type: "POST",
        aync : true,

        contentType:'application/json',
        dataType:'json',

        data: JSON.stringify(data_file),

        success : onSuccess,
    });
}

function asyncSavePreset(name, preset, onSuccess, onError) {
    return $.ajax({
      url: "/preset/save",

      type: "POST",

      contentType:'application/json',
      dataType:'json',

      data: JSON.stringify({
        name: name,
        preset: preset
      }),

      success: onSuccess,
      error: onError,
    })
}


function asyncDeletePreset(presets, onSuccess, onError) {
    return $.ajax({
      url: "/preset/delete",

      type: "POST",

      contentType:'application/json',
      dataType:'json',

      data: JSON.stringify(presets),

      success: onSuccess,
      error: onError,
    })
}
