// holds all the file-explorer creation and update functions


var currDir;                //holds the current directory- a list of folders
var patt = /\\[^\\]+$/;


$(document).ready(function() {


  $('#loader').hide();
  //get root path
  var empty = [];
  callListdir(empty,drawTree);
  //fixes explorer height to fill whole screen
  maxHeight('#file-explorer');

 
  //handles file explorer double-click event
  $('#jstree').bind("dblclick.jstree", function (event) {
   //var node = $(event.target).closest("li");
   var node = $('#jstree').jstree('get_selected',true);
   //if folder - update tree
   if(node[0].type == 'default'){
   	var url = node[0].id;
   	currDir = url;
   	callListdir(url,updateTree);
   }else{
   	  //do nothing - file is selected
   }
  });

  //handles file explorer 'up directory' button
  $('#up-dir').on('click',function(){
    id = currDir.replace(patt, "");  
    currDir = id;
    callListdir(currDir + "\\",updateTree);
  });

  //handles project selection- 'accept' button
  $('#proj-select').on('click', sendExperimentToServer);

  //toggles file explorer
  $( "#toggle-explorer" ).click(function() {
    $("#explorer-wrapper").toggle( "slide");
    $("#toggle-explorer i").toggleClass("glyphicon-arrow-left glyphicon-arrow-right");
  });


});

//sends the selected experiment path to the server to get the experiment parameters
//upon success, moves to handleParameters which generates the corresponding UI
function sendExperimentToServer(){
  //get the path of the project
    var node = $('#jstree').jstree('get_selected',true);
    var id = node[0].id;

    //if selection is valid (not a folder)
    if(isValid(node[0])){
      //get parameter list from the server, and fill parameters list
      url = "/getcolumns?experiment="+id;
      $('#loader').show();

      //send to server
      $.ajax({
        url: url,
        success: handleParameters,
        error: serverErrorHandler
      });
    }
}


//makes a request to the server to get the tree information with the given url
//if the request was successful, the success function is then called
function callListdir(data,successFunction){
  $.ajax({
        async : true,
        type : "POST",
        url : "/listdir",
        contentType:'application/json',
        data: JSON.stringify(data),
        dataType : "json",    
        success : successFunction      
    });
}

//checks that the selected id is indeed a file-type
function isValid(node){
  if(node.type == 'file'){
    return true;
  }else{
    return false;
  }
}

//updates the tree with new data
function updateTree(data){
  $('#jstree').jstree(true).settings.core.data = data.json;
  $('#jstree').jstree(true).refresh();
}

//draws the initial tree with the data received from the server - called once
function drawTree(data){
  $(function() {
      $('#jstree')
        .jstree({
          'core' : {
            'data' : data.json,
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
          'plugins' : ['state','dnd','sort','types','contextmenu','unique']
        })
      });
  //init currdir with directory of the first node
  currDir = data.url;
}

//fixes the height 
function maxHeight(div){
	var header_height = 100;
	var remaining_height = parseInt($(window).height() - header_height); 
	$(div).height(remaining_height); 
}