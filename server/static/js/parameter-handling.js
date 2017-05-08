// Author: Hadas Shahar <hshaha05@campus.haifa.ac.il>
///////////holds all the Graph Generation functions///////////////////////

///global variables:

var graphData;         //holds the received server response when user selects a project
var selectedModel;     //holds the selected graph model
var presets;           //holds the presets received from the server


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
    selectedModel = $('#models').val();
    generateGraphParameters(graphData, selectedModel); 
  });

  //add listener to plugin reload button- reload the plugins and refresh the model list
  $('#reload-plugins').click(function(){
    $("#err-msg").hide();
    //reload plugins and refresh the model list
    $.when( $.ajax({
      type: "GET",
      url: "/reloadplugin"
    })).then(sendExperimentToServer);
  });

  //add listener to preset select button
  $('#preset-list').change(function(){
    $('#select-preset').removeClass('disabled');
    $('#delete-preset').removeClass('disabled');
  });

  //add listener to preset select button
  $('#select-preset').click(function(){
    $('#loader').show();
    var selectedPreset = $('#preset-list').val();
    var reg = /^(.*)\:\s{6}/g;
    var presetName = reg.exec(selectedPreset)[1];
    if(presetName != null){
      sendParametersToServer(presets[presetName]);
    }else{
      $('#notification').html("couldn't parse preset name out of selected preset");
    }
    
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
    //send save command to the sever and then refresh the preset list
    $.when( $.ajax({
      type: "POST",
      url: "/save",
      success: displayOkMessage,
      error: serverErrorHandler,
      contentType:'application/json',
      data: JSON.stringify(savedPreset),
      dataType:'json'
    }) ).then(getPresetList);

    //clear input and hide save as dialog
    $('#preset-name').val('');
    $('#save-as-wrapper').hide();

  });

  $('#delete-preset').click(function(){
    var selectedPreset = [$('#preset-list').val()];
    //send delete command to the sever and then refresh the preset list
    $.when( $.ajax({
      type: "POST",
      url: "/delete",
      success: displayOkMessage,
      error: serverErrorHandler,
      contentType:'application/json',
      data: JSON.stringify(selectedPreset),
      dataType:'json'
    })).then(getPresetList);
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


  }catch(e){
  $("#notification").html(e.message);
}
});



///functions:

//gathers all the parameters from the parameters form and returns a json
//"{"Line":{"x_axis":"timestamp","y_axis":"performance","group_by":{"name":["vm-1","vm-2"]}}}"
function fetchParameters(){
  //get the parameters (deep copy)
  var modelParamJson = $.extend( true, {}, graphData.models[selectedModel] );

  //for each parameter,  fill the json with the actual value
  $.each(graphData.models[selectedModel],function(key,value){

    switch(value.type){
      case 'single':
        var selectedColumn = $('#input-'+key).val();
        //if we allow user to select a value in the column, send the column + value
        if(value.filterByValue){
          var selectedValue = $('#input-'+key+"-val-select").val();
          var dict = {};
          dict[selectedColumn] = selectedValue;
          modelParamJson[key] = dict;
        }
        //if not- send only the column name
        else{
          modelParamJson[key] = selectedColumn;
        }
        break;
      case 'multiple':
        var selectedColumn = $('#input-'+key).val();
        //get all the selected values
        var allSelectedValues = [];
        $('#input-'+key+'-val-select :selected').each(function(i, selected){
          allSelectedValues[i] = $(selected).text();
        });
        var dict = {};
        dict[selectedColumn] = allSelectedValues;
        modelParamJson[key] = dict;
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
  console.log("sending selected parameters to the server - awaiting response");
  $("#notification").html("sending selected parameters to the server - awaiting response");

  var modelParamJson = fetchParameters();
  //compile parameter json
  sendParametersToServer(modelParamJson);
}

//sends the selected parameters to the server to plot
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

//fills the model list and moves to the parameters tab - called when server returns selected experiment info
function handleParameters(data){
  console.log("received response from the server");
  $("#notification").html("received response from the server - please select a model or load a preset");
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
  var result = [];

  //will display the name, followed by spaces, and the preset values
  for (var key in data) {
    result.push(key +":\xa0\xa0\xa0\xa0\xa0\xa0\xa0" + JSON.stringify(data[key])+"'");
  }

  fillListParameters($('#preset-list'),result);
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
    var input = generateInputField(key,"single",data.cols);

    var formDiv = wrapInDiv([label,input],'form-group row');
    $('#parameter-selection').append(formDiv);
    //if we want to add an option to select a specific value
    if(value.filterByValue){
      //when the column is selected, 
      //fetch the actual parameters from the server 
      //and allow the user to select a specific value
      $('#input-'+key).on('input', function(){
        //get the datalist id
        var key = this.id.replace('input-','');
        //if option exists
        if(findInDatalist(key,this.value)){
          var data = {'key':key,'parameters':this.value};
          console.log('requesting values of column '+this.value+' from server');
          $("#notification").html('requesting values of column '+this.value+' from server');
          $.ajax({
            aync : true,
            url : "/getvals",
            type: "POST",
            contentType:'application/json',
            data: JSON.stringify(data),
            dataType:'json',
            success :  AddSelectByValue   
          });
        }
      });
    }
  });
}




//when receiving the sepecific column actual parameters,
//creates a dropdown with said parameters allowing the user to select by value
//{key:'parent-id',parameters:[1,2,3,4,..]}
function AddSelectByValue(data){
  console.log('received values from server,generating sub-input field');
  $("#notification").html('received values from server,generating sub-input field');
  var type = graphData.models[selectedModel][data.key].type;
  //create new input field and populate it
  var input = generateInputField(data.key+'-val-select',type,data.parameters,false);
  //if element already exists- update it with new content
  if($('#input-'+data.key+'-val-select').length){
    $('#input-'+data.key+'-val-select').replaceWith(input);
  }else{
    //if not - append new element to parent
    $('#input-'+data.key).after(input);
  }
}


//////////////helper functions
//finds a given value in a datalist with the given id
function findInDatalist(id,value){
  var options = $('#'+id+" option");
  var isFound = false;
  $.each(options, function(i,val){
    if(val.innerHTML == value){
      isFound = true;
    }
  });
  return isFound;
}

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
        if($('#input-'+key+'-val-select :selected').length == 0){
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
