// @edited: Liran Funaro <funaro@cs.technion.ac.il>
// @author: Hadas Shahar <hshaha05@campus.haifa.ac.il>

///////////holds all the Graph Generation functions///////////////////////

///global variables:

var selectedModelParameters;
var selectedFileCols;  //holds the received server response when user selects a project


///on document ready:

$(document).ready(function() {
  try{
  //hide message
  resetDisplay();
  fixHeight();

  ////binding- adding listeners to click events

  $('#param-select').click(sendPlotRequestFromUserInput);

  $('#parameters-form').change(function(){
    if(isParametersFormValid()){
      $('#param-select').removeClass('disabled');
      $('#save-preset').removeClass('disabled');
    }else{
      $('#param-select').addClass('disabled');
      $('#save-preset').addClass('disabled');
    }
  });

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
function fetchFormParameters() {
  //get the parameters (deep copy)
  var modelParamJson = $.extend( true, {}, selectedModelParameters );

  //for each parameter,  fill the json with the actual value
  $.each(selectedModelParameters, function(key, value){

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

  return {
    graph_type: selectedModel,
    parameters: modelParamJson,
  }
}


//collects all the graph parameters selected by the user,
//generates a json and sends to the server
function sendPlotRequestFromUserInput(){
  //show loader animation
  $("#loader").show();
  console.log("sending selected parameters to the server - awaiting response");
  $("#notification").html("sending selected parameters to the server - awaiting response");

  //compile parameters and send
  var modelParamJson = fetchFormParameters();
  sendPlotRequest(modelParamJson);
}

//generates the required graph parameters 
//-creates the required input fields based on the selected model
function generateModelParameters(model) {
  $('#parameter-selection').empty();
  var newP = generateParagraph("Select graph parameters:");
  $('#parameter-selection').append(newP);

  $.when(
    asyncGetColumns(selectedFile, function(cols) {
      selectedFileCols = cols;
    }, serverErrorHandler),
    asyncPluginParameters(model, function(parameters) {
      selectedModelParameters = parameters;
    }),
  ).then(function() {

    //go over all the model parameters, generate an input field and fill in the input parameters
    $.each(selectedModelParameters, function(key, value){
      var label = generateLabel(key,'col-xs-2 col-form-label',key);
      var input = generateInputField(key,"single", selectedFileCols);

      var formDiv = wrapInDiv([label,input],'form-group row');
      $('#parameter-selection').append(formDiv);
      //if we want to add an option to select a specific value
      if(value.filterByValue) {

        //when the column is selected, 
        //fetch the actual parameters from the server 
        //and allow the user to select a specific value
        $('#input-'+key).on('input', function(){
          //get the datalist id
          var key = this.id.replace('input-','');
          //if option exists
          if(findInDatalist(key,this.value)){
            console.log('requesting values of column '+this.value+' from server');
            $("#notification").html('requesting values of column '+this.value+' from server');
            asyncGetValues(selectedFile, this.value, function(parameters) {
              AddSelectByValue(key, parameters);
            });
          }
        });

      }

    });

  })
}


//when receiving the sepecific column actual parameters,
//creates a dropdown with said parameters allowing the user to select by value
//{key:'parent-id',parameters:[1,2,3,4,..]}
function AddSelectByValue(key, parameters){
  console.log('received values from server,generating sub-input field');
  $("#notification").html('received values from server,generating sub-input field');
  var type = selectedModelParameters[key].type;
  //create new input field and populate it
  var input = generateInputField(key+'-val-select',type, parameters,false);
  //if element already exists- update it with new content
  if($('#input-'+key+'-val-select').length){
    $('#input-'+key+'-val-select').replaceWith(input);
  }else{
    //if not - append new element to parent
    $('#input-'+key).after(input);
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

//returns true if form is filled, and false otherwise
function isParametersFormValid(){
  var isValid = true;
  //for each parameter,  fill the json with the actual value
  $.each(selectedModelParameters, function(key,value){

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
