///////////holds all the Graph Generation functions///////////////////////

//global variables
var graphData;         //holds the received server response when user selects a project
var selectedModel;     //holds the selected graph model
var presets;           //holds the presets received from the server

//on document ready
$(document).ready(function() {
  //hide message
  resetDisplay();
  fixHeight();
  
  //add listerer to models selection - once a model is click, create the necessary input parameters
  $("#models").on('input', function () {
    $("#err-msg").hide();
    selectedModel = $('#models').val();
    generateGraphParameters(graphData, selectedModel); 
  });

  //add listener to plugin reload button- reload the plugins and refresh the model list
  $('#reload-plugins').click(function(){
    $("#err-msg").hide();
    //reload plugins
    $.ajax({
      type: "GET",
      url: "/reloadplugin"
    });
    //refresh models list
    sendExperimentToServer();
  });

  //add listener to preset select button
  $('#preset-list').change(function(){
    $('#select-preset').removeClass('disabled');
    $('#delete-preset').removeClass('disabled');
  });

  //add listener to preset select button
  $('#select-preset').click(function(){
    var selectedPreset = $('#preset-list').val();
    sendParametersToServer(presets[selectedPreset]);
  });

  $('#param-select').click(fetchParametersAndGetGraph);

  //save dialog functions
  $('#save-preset').click(function(){
    $('#save-as-wrapper').show();
  });

  $('#save-as-cancel').click(function(){
    $('#preset-name').val('');
    $('#save-as-wrapper').hide();
  });

  $('#save-as-ok').click(function(){
    var presetName = $('#preset-name').val();
    //get all other preset parameters and send to server
    var presetParameters = fetchParameters();
    var savedPreset = {'name':presetName, 'preset':presetParameters};
    $.ajax({
      type: "POST",
      url: "/save",
      success: displayOkMessage,
      error: serverErrorHandler,
      contentType:'application/json',
      data: JSON.stringify(savedPreset),
      dataType:'json'
    });
    getPresetList();
    //clear input and hide save as dialog
    $('#preset-name').val('');
    $('#save-as-wrapper').hide();

  });

  $('#delete-preset').click(function(){
    var selectedPreset = [$('#preset-list').val()];
    $.ajax({
      type: "POST",
      url: "/delete",
      success: displayOkMessage,
      error: serverErrorHandler,
      contentType:'application/json',
      data: JSON.stringify(selectedPreset),
      dataType:'json'
    });
    getPresetList();
  });

  $('#parameters-form').change(function(){
    if(isParametersFormValid()){
      $('#param-select').removeClass('disabled');
      $('#save-preset').removeClass('disabled');
    }else{
      $('#param-select').addClass('disabled');
      $('#save-preset').addClass('disabled');
    }
  });

  $('#reload-preset').click(getPresetList);

  //prevent page reload on form send
  $("form").on("submit", function (e) {
    e.preventDefault();
  });
});

//gathers all the parameters from the parameters form and returns a json
function fetchParameters(){
  //get the parameters (deep copy)
  var modelParamJson = $.extend( true, {}, graphData.models[selectedModel] );

  //for each parameter,  fill the json with the actual value
  $.each(graphData.models[selectedModel],function(key,value){
    switch(value.type){
      case 'single':
        modelParamJson[key] = $('#input-'+key).val();
        break;
      case 'multiple':
        //get all the selected values
        var allSelectedValues = [];
        $('#input-'+key+' :selected').each(function(i, selected){
          allSelectedValues[i] = $(selected).text();
        });
        //put in json
        modelParamJson[key] = allSelectedValues;
        break;
      case 'radio':
        modelParamJson[key] = $('#input-'+key).val();
        break;
      case 'checkbox':
        //get all the checked values
        var allCheckedValues = [];
        $('#input-'+key+' :selected').each(function(i, checked){
          allCheckedValues[i] = $(checked).text();
        });
        break;
      case 'range':
        //add handling
        break;
    }
  });

  var json = {};
  json[selectedModel] = modelParamJson;
  return json;
}


//collects all the graph parameters selected by the user,
//generates a json and sends to the server
function fetchParametersAndGetGraph(){
  //show loader animation
  $("#loader").show();
  console.log("sending selected parameters to the server");

  var modelParamJson = fetchParameters();
  //compile parameter json
  sendParametersToServer(modelParamJson);
}

//sends the given parameters to the server
function sendParametersToServer(data){
  //send to server to generate graph
  $.ajax({
      type: "POST",
      url: "/plot",
      success: displayGraph,
      error: serverErrorHandler,
      contentType:'application/json',
      data: JSON.stringify(data),
      dataType:'json'
    });
}

//display the graph received from the server
function displayGraph(data){
  //hide error message (if present)
  $("#graph-display").empty();

  var div = data.div;
  var js = data.js;

  $("#graph-display").append(div);
  $.getScript(js); 
  //switch to graph display tab
  $('.nav-pills a[href="#graph-display"]').tab('show');
  //hide loader animation
  resetDisplay();
}

//fills the model list and moves to the parameters tab - called when server returns selected experiment info
function handleParameters(data){
  graphData = data;

  fillModelListImages(data.models);
  getPresetList();
  $('.nav-pills a[href="#graph-selection"]').tab('show');
  $('.nav-pills a[href="#create-new"]').tab('show');
  $('#model-select').removeClass('disabled');
  resetDisplay();
}

//fills the model list with available models and images
function fillModelListImages(data){
  var modelsList = Object.keys(data);
  $('#model-list').empty();

  $.each(modelsList, function(i,value){
    //generate li element with image and model name
    var newImage = document.createElement("img");
    //if image exists- use image,  otherwise use default image
    newImage.setAttribute('src','img/pluginImg/'+value+'.png');
    newImage.setAttribute('onerror',"this.onerror=null;this.src='img/defaultLogo.png';");
    var newP = generateParagraph(value);

    var newLi = document.createElement("li");
    newLi.append(newImage);
    newLi.append(newP);
    newLi.setAttribute('name',value);

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
    selectedModel = this.textContent;
    generateGraphParameters(graphData, selectedModel);
  });
}

//requests the preset list from the server - used to fill the 'load' section
function getPresetList(){
  var empty = [];
  $.ajax({
        aync : true,
        url : "/load",
        type: "POST",
        contentType:'application/json',
        data: JSON.stringify(empty),
        dataType:'json',
        success : fillPresetList       
    });
}

//fills the preset list with the response from the server
function fillPresetList(data){
  presets = data;
  var nameList = Object.keys(data);
  nameList.sort();
  fillListParameters($('#preset-list'),nameList);
}


//generates the required graph parameters 
//-creates the required input fields based on the selected model
function generateGraphParameters(data, model){
  $('#parameter-selection').empty();
  var newP = generateParagraph("Select graph parameters:");
  $('#parameter-selection').append(newP);

  //go over all the model parameters, generate an input field and fill in the input parameters
  $.each(data.models[model], function(key,value){
    var label = generateLabel(key,'col-xs-2 col-form-label',key);
    var input = generateInputField(key,value.type,data[value.source]);

    var formDiv = wrapInDiv([label,input],'form-group row');

    $('#parameter-selection').append(formDiv);
  });

}

//////////////helper functions


//fixes the height of the graph display tab
function fixHeight(){
  remaining_height = parseInt($(window).height() - 250); 
  $('#graph-display').height(remaining_height); 
}

//resets the display - hides loaders and error messages
function resetDisplay(){
  //hide divs
  $("#err-msg").hide();
  $('#save-as-wrapper').hide();
  $('#server-success').hide();
  $('#loader').hide();
}

//returns true if form is filled, and false otherwise
function isParametersFormValid(){
  var isValid = true;
  //for each parameter,  fill the json with the actual value
  $.each(graphData.models[selectedModel],function(key,value){
    switch(value.type){
      case 'single':
        if($('#input-'+key).val() === ''){
          isValid=false;
        };
        break;
      case 'multiple':
        if($('#input-'+key+' :selected').length == 0){
          isValid=false;
        }
        break;
      case 'radio':
        if($('#input-'+key).val() === ''){
          isValid=false;
        };
        break;
      case 'checkbox':
        //get all the checked values
        var allCheckedValues = [];
        $('#input-'+key+' :selected').each(function(i, checked){
          allCheckedValues[i] = $(checked).text();
        });
        break;
      case 'range':
        //add handling
        break;
    }
  });

  return isValid;
}

//displays an error message
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

