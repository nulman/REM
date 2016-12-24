var app = angular.module('store', [ ]);
var currDir;
var patt = /\\[^\\]+$/;

$(document).ready(function() {

  //treeScript();
  //get root path
  callUrl("");
  fixHeight();

  

  $('#jstree').bind("dblclick.jstree", function (event) {
   var node = $(event.target).closest("li");
   var url = node[0].id;
   currDir = url
   callUrlUpdate(url)

  });

  $('#up-dir').on('click',function(){
    id = currDir.replace(patt, "");  
    currDir = id;
    callUrlUpdate(currDir + "\\");
  });

  //handles project selection
  $('#proj-select').on('click', function () {
    //get the path of the project
    var node = $('#jstree').jstree('get_selected');
    var id = node[0];

    //if selection is valid (not a folder)
    if(isValid(id)){
      //get parameter list from the server, and fill parameters list
      url = "/getcolumns?experiment="+id;
      //$.get( url, fillProjectParameters);
      $.ajax({
        url: url,
        success: fillProjectParameters,
        error: serverErrorHandler
      });
    }
  });


  //handles parameter selection
  $('#param-select').on('click', function () {
    //get the path of the project
    var x = $('#input-x').val();
    var y = $('#input-y').val();
    var machine = $('#input-machine').val();

    //get parameter list from the server, and fill parameters list
    url = "/plot?x="+x+"&y="+y+"&machines="+machine;
    $.get( url, displayGraph);

  });

  $("form").on("submit", function (e) {
    e.preventDefault();
  });
});


//makes the request to the server with the given url
//then draws the tree with the response json
function callUrl(url){
  $.ajax({
        async : true,
        type : "GET",
        url : "/listdir?id=" + url,
        dataType : "json",    

        success : drawTreeWithJson      
    });
}

function callUrlUpdate(url){
  $.ajax({
        async : true,
        type : "GET",
        url : "/listdir?id=" + url,
        dataType : "json",    

        success : updateTreeWithJson      
    });
}

//checks that the selected id is indeed a file-type
function isValid(id){
  // var node = $('#jstree').find("[id="+id+"]")
  // if(get_type(node) == "file"){
  //   return true;
  // }else{
  //   return false;
  // }
  return true;
}

function updateTreeWithJson(data){
  $('#jstree').jstree(true).settings.core.data = data;
  $('#jstree').jstree(true).refresh();
}


function displayGraph(data){
  //hide error message (if present)
  $("#err-msg").addClass("hidden");

  var div = data.div;
  var js = data.js;

  console.log(div);
  console.log(js);

  //$("#graph-display").load(div);
  $("#graph-display").append(div);
  $.getScript(js); 

  $('.nav-pills a[href="#graph-display"]').tab('show');
}

function serverErrorHandler(data){
  $("#err-msg").removeClass("hidden");
}

//receives a json list of parameters and puts them in the x/y/machines parameters list
function fillProjectParameters(data){
  //hide error message (if present)
  $("#err-msg").addClass("hidden");
  //delete previous options information
  $("#x-axis").empty();
  $("#y-axis").empty();
  $("#machines").empty();

  //fill parameter options
  $.each(data.cols, function(i, value) {
    $('#x-axis').append($('<option>').text(value).attr('value', value));
    $('#y-axis').append($('<option>').text(value).attr('value', value));
  });
  $.each(data.machines, function(i,value){
    $("#machines").append($("<option>").text(value).attr("value",value));
  })

  $('.nav-pills a[href="#parameter-selection"]').tab('show');
}

//fixes the height 
function fixHeight(){
  remaining_height = parseInt($(window).height() - 300); 
  $('#graph-display').height(remaining_height); 
}

function drawTree(url){
  $(function() {
      $('#jstree')
        .jstree({
          'core' : {
            'data' : {
              'url' : url,
              "dataType" : "json",
              'data' : function (node) {
                return { 'id' : node.id };
              }              
            },
            'themes' : {
              "name": "default-dark",
              "dots": true,
              "icons": true,
              'responsive' : false,
              'variant' : 'small',
              'stripes' : true
            }
          },
          'sort' : function(a, b) {
            return this.get_type(a) === this.get_type(b) ? (this.get_text(a) > this.get_text(b) ? 1 : -1) : (this.get_type(a) >= this.get_type(b) ? 1 : -1);
          },
          
          'types' : {
            'default' : { 'icon' : 'folder' },
            'file' : { 'valid_children' : [], 'icon' : 'file' }
          },
          'unique' : {
            'duplicate' : function (name, counter) {
              return name + ' ' + counter;
            }
          },
          'plugins' : ['state','dnd','sort','types','contextmenu','unique']
        })
      });
}

function drawTreeWithJson(json){
  $(function() {
      $('#jstree')
        .jstree({
          'core' : {
            'data' : json,
            'themes' : {
              "name": "default-dark",
              "dots": true,
              "icons": true,
              'responsive' : false,
              'variant' : 'small',
              'stripes' : true
            }
          },
          'sort' : function(a, b) {
            return this.get_type(a) === this.get_type(b) ? (this.get_text(a) > this.get_text(b) ? 1 : -1) : (this.get_type(a) >= this.get_type(b) ? 1 : -1);
          },
          
          'types' : {
            'default' : { 'icon' : 'folder' },
            'file' : { 'valid_children' : [], 'icon' : 'file' }
          },
          'unique' : {
            'duplicate' : function (name, counter) {
              return name + ' ' + counter;
            }
          },
          'plugins' : ['state','dnd','sort','types','contextmenu','unique']
        })
      });
}


//generates the file explorer tree 
function treeScript(){

    $(function() {
      
      var url = "/listdir"
      $('#jstree')
        .jstree({
          'core' : {
            'data' : {
              'url' : url,
              'data' : function (node) {
                return { 'id' : node.id };
              }
            },
            'themes' : {
              "name": "default-dark",
              "dots": true,
              "icons": true,
              'responsive' : false,
              'variant' : 'small',
              'stripes' : true
            }
          },
          'sort' : function(a, b) {
            return this.get_type(a) === this.get_type(b) ? (this.get_text(a) > this.get_text(b) ? 1 : -1) : (this.get_type(a) >= this.get_type(b) ? 1 : -1);
          },
          
          'types' : {
            'default' : { 'icon' : 'folder' },
            'file' : { 'valid_children' : [], 'icon' : 'file' }
          },
          'unique' : {
            'duplicate' : function (name, counter) {
              return name + ' ' + counter;
            }
          },
          'plugins' : ['state','dnd','sort','types','contextmenu','unique']
        })
      });
}