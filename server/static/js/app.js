$(document).ready(function() {

  fixHeight();
  $("#err-msg").hide();

  //handles parameter selection
  $('#param-select').on('click', function () {
    $("#loader").show();
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


function displayGraph(data){
  //hide error message (if present)
  $("#err-msg").addClass("hidden");
  $("#graph-display").empty();

  var div = data.div;
  var js = data.js;

  console.log(div);
  console.log(js);

  //$("#graph-display").load(div);
  $("#graph-display").append(div);
  $.getScript(js); 

  $('.nav-pills a[href="#graph-display"]').tab('show');
  $("#loader").hide();
}

function serverErrorHandler(data){
  $('#err-msg').append(data);
  $('#loader').hide();
  $("#err-msg").show();
}

//receives a json list of parameters and puts them in the x/y/machines parameters list
function fillProjectParameters(data){
  //hide error message (if present)
  $("#err-msg").hide();
  //save types info
  var x = $("#x-axis").val();
  var y = $("#y-axis").val();
  var machine = $("#machines").val();
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

  if(x != ""){
    $("#x-axis").val(x);
  }
  if( y != ""){
    $("#y-axis").val(y);
  }
  if( machine != ""){
    $("#machines").val(machine);
  }

  $('.nav-pills a[href="#parameter-selection"]').tab('show');

  $("#param-select").removeClass('disabled');
  $('#loader').hide();
}

//fixes the height 
function fixHeight(){
  remaining_height = parseInt($(window).height() - 250); 
  $('#graph-display').height(remaining_height); 
}

