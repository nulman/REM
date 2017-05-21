// @edited: Liran Funaro <funaro@cs.technion.ac.il>
// @author: Hadas Shahar <hshaha05@campus.haifa.ac.il>

////////// holds all the file-explorer creation and update functions ////////

///global variables:

var curDir = "";                //holds the current directory- a list of folders
var curDirList = [];
var selectedFile = "";

///on document ready:

$(document).ready(function() {
  try{
  //hide unnecesary information
  $('#loader').hide();
  $('#selected-exp').hide();

  //get root directory and draw the initial file explorer tree
  initTree();
  changeDir(curDirList);

  //fixes explorer height to fill whole screen
  maxHeight('#file-explorer');

 
  ////binding- adding listeners to click events
  
  $( "#explorer-wrapper" ).resizable({
    handles: 'n,w,s,e',minWidth: 200,
    containment: ".row"
  });

  //reloads the page when clicking on the logo
  $('#logo').on('click',function(){
    location.reload();
  });

  //handles file explorer double-click event
  $('#jstree').bind("dblclick.jstree", function (event) {
     //var node = $(event.target).closest("li");
     var node = $('#jstree').jstree('get_selected',true);
     //if folder - update tree
     if(node[0].type == 'default'){
     	changeDir([node[0].id]);
     }else{
        selectDataFile();
     }
  });

  //handles file explorer 'up directory' button
  $('#up-dir').on('click',function(){
    up_dir_list = curDirList.slice(0, -1);
    changeDir(up_dir_list);
  });

  //handles project selection- 'OK' button
  $('#proj-select').on('click', selectDataFile);

  //toggles file explorer button
  $( "#toggle-explorer" ).click(function() {
    $("#explorer-wrapper").toggle( "slide");
    $("#toggle-explorer i").toggleClass("glyphicon-arrow-left glyphicon-arrow-right");
  });

  ////end of binding

}catch(e){
  $("#notification").html(e.message);
}
});


///functions:

//sends the selected experiment path to the server to get the experiment parameters
//upon success, moves to handleParameters which generates the corresponding UI
function selectDataFile() {
  //get the path of the project
    var node = $('#jstree').jstree('get_selected',true)[0];
    if(node.type != 'file') {
        return
    }
    selectDataFileSequance(node.id);
}

//sends the selected experiment path to the server to get the experiment parameters
//upon success, moves to handleParameters which generates the corresponding UI
function selectDataFileSequance(path) {
    selectedFile = path;
    $('#selected-exp').html(selectedFile);
    $('#selected-exp').show();

    //get parameter list from the server, and fill parameters list
    $('#loader').show();
    console.log("sending experiment to the server, awaiting response");
    $("#notification").html("sending experiment to the server, awaiting response");
    //clear the current model/parameters form

    updateListPlugin()
    updatePresetList()
}


//makes a request to the server to get the tree information with the given url
//if the request was successful, the success function is then called
function changeDir(path_list) {
  asyncListDir(path_list, function(data) {
    //updates the tree with new data
    curDirList = data.url_list;
    curDir = data.url;
    $('#jstree').jstree(true).settings.core.data = data.json;
    $('#jstree').jstree(true).refresh();
    $('#curr-dir').html(curDir);
  });
}


function initTree() {
    $('#jstree').jstree({
      'core' : {
        'data' : [],
        'themes' : {
          "name": "default-dark",
          //"dots": true,
          "icons": true,
          'responsive' : false,
          //'variant' : 'small',
          'stripes' : true
        }
      },
      'sort' : function(a, b) {
        return this.get_type(a) === this.get_type(b) ? (this.get_text(a) > this.get_text(b) ? 1 : -1) : (this.get_type(a) >= this.get_type(b) ? 1 : -1);
      },
      'types' : {
        'default' : { 'icon' : 'glyphicon glyphicon-folder' },
        'file' : { 'valid_children' : [], 'icon' : 'glyphicon glyphicon-file' }
      },
      'unique' : {
        'duplicate' : function (name, counter) {
          return name + ' ' + counter;
        }
      },
      'plugins' : ['state','dnd','sort','types','unique','wholerow']
    })
}


//fixes the height 
function maxHeight(div){
	var header_height = 100;
	var remaining_height = parseInt($(window).height() - header_height); 
	$(div).height(remaining_height); 
}