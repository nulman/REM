// @edited: Liran Funaro <funaro@cs.technion.ac.il>
// @author: Hadas Shahar <hshaha05@campus.haifa.ac.il>

///////////holds all the Graph Generation functions///////////////////////

///global variables:

var selectedModel;     //holds the selected graph model


///on document ready:

$(document).ready(function() {
  try{
  //hide message
  resetDisplay();
  fixHeight();

  ////binding- adding listeners to click events

  //add listerer to models selection - once a model is click, create the necessary input parameters
  $("#models").on('input', function () {
    $("#err-msg").hide();
    selectModel($('#models').val()); 
  });

  //add listener to plugin reload button- reload the plugins and refresh the model list
  $('#reload-plugins').click(function(){
    $("#err-msg").hide();
    updateListPlugin(true);
  });

  }catch(e){
  $("#notification").html(e.message);
}
});



///functions:

function updateListPlugin(reload=false) {
  $('model-list').empty();
  $('#parameter-selection').empty();
  asyncListPlugin(reload, handleModulesList)
}

function selectModel(model) {
  selectedModel = model
  generateModelParameters(model)
}



//fills the model list with available models and images
function handleModulesList(modelsData) {
  $("#notification").html("Received models response from the server.");
  $('#model-list').empty();

  $.each(modelsData, function(modelName, modelImage){
    //generate li element with image and model name
    var newImage = document.createElement("img");
    //if image exists- use image,  otherwise use default image
    newImage.setAttribute('src', modelImage);
    newImage.setAttribute('onerror',"this.onerror=null;this.src='img/defaultLogo.png';");
    var newP = generateParagraph(modelName);

    var newLi = document.createElement("li");
    newLi.append(newImage);
    newLi.append(newP);
    newLi.setAttribute('name', modelName);

    //append new li
    $('#model-list').append(newLi);
  });

  //handling model selection (li click event)
  $("#model-list li").on("click",function() {
    //remove all other highlights
    $("#model-list li").removeClass('highlight');
    //add highlight to selected
    $(this).addClass('highlight');
    //generate the graph parameters
    selectModel(this.textContent);
  });

  $('.nav-pills a[href="#graph-selection"]').tab('show');
  $('.nav-pills a[href="#create-new"]').tab('show');
  $('#model-select').removeClass('disabled');

  resetDisplay();
}



//resets the display - hides loaders and error messages
function resetDisplay(){
  //hide divs
  $("#err-msg").hide();
  $('#save-as-wrapper').hide();
  $('#server-success').hide();
  $('#loader').hide();
}

//displays an error message from the server
function serverErrorHandler(data){
  $('#err-msg').html(data.responseText);
  $('#loader').hide();
  $("#err-msg").show();
}

//displays the ok message received from the server - disappears after 5 sec
function displayOkMessage(message){
  $('#server-success').html(message[0]);
  $('#server-success').show();
  $('#server-success').fadeOut(5000);
}
