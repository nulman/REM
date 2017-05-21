// @edited: Liran Funaro <funaro@cs.technion.ac.il>
// @author: Hadas Shahar <hshaha05@campus.haifa.ac.il>


//sends the selected parameters to the server to plot
function sendPlotRequest(data) {
  //send to server to generate graph
  asyncPlot(selectedFile, data.graph_type, data.parameters,
    displayGraph, serverErrorHandler)
}

//display the graph received from the server
function displayGraph(data) {
  //hide error message (if present)
  console.log("received response- displaying graph");
  $("#notification").html("received response- displaying graph");
  $("#graph-display").empty();

  var div = data.div;
  var js = data.js;

  $("#graph-display").append(div);
  eval(js);
  //switch to graph display tab
  $('.nav-pills a[href="#graph-display"]').tab('show');
  //hide loader animation
  resetDisplay();
}


//fixes the height of the graph display tab
function fixHeight(){
  remaining_height = parseInt($(window).height() - 250); 
  $('#graph-display').height(remaining_height); 
}