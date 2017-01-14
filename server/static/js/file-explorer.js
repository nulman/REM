// holds all the file-explorer creation and update functions


var currDir;                //holds the current directory
var patt = /\\[^\\]+$/;


$(document).ready(function() {


  $('#loader').hide();
  //get root path
  callUrl("");
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
   	callUrlUpdate(url);
   }else{
   	  //do nothing - file is selected

   }
  });

  //handles file explorer 'up directory' button
  $('#up-dir').on('click',function(){
    id = currDir.replace(patt, "");  
    currDir = id;
    callUrlUpdate(currDir + "\\");
  });

  //handles project selection- 'accept' button
  $('#proj-select').on('click', function () {
    //get the path of the project
    var node = $('#jstree').jstree('get_selected',true);
    var id = node[0].id;

    //if selection is valid (not a folder)
    if(isValid(node[0])){
      //get parameter list from the server, and fill parameters list
      url = "/getcolumns?experiment="+id;
      $('#loader').show();
      $("#param-select").addClass('disabled');

      $.ajax({
        url: url,
        success: handleParameters,
        error: serverErrorHandler
      });
    }
  });

  var duration = 'slow';

  //toggles file explorer
  $( "#toggle-explorer" ).click(function() {
    $("#explorer-wrapper").toggle( "slide");
    
    // $('#toggle-explorer').empty();
    // $('#toggle-explorer').append('<i class="glyphicon glyphicon-arrow-right white"></i>');
  });


});


//makes the request to the server with the given url
//then draws the tree with the response json
function callUrl(url){
  $.ajax({
        aync : true,
        type : "GET",
        url : "/listdir?id=" + url,
        dataType : "json",    

        success : drawTree      
    });
}

//makes the request to the server with the given url
//then updates the existing tree with the response json
function callUrlUpdate(url){
  $.ajax({
        async : true,
        type : "GET",
        url : "/listdir?id=" + url,
        dataType : "json",    

        success : updateTree      
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

//draws the initial tree
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