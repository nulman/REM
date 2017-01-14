var graphData = "";         //holds the received server response when user selects a project
var selectedModel = "";     //holds the selected graph model

$(document).ready(function() {

  $("#err-msg").hide();
  fixHeight();

  //handles model selection
  // $('#model-select').on('click',function(){
  //   selectedModel = $('#input-models').val();
  //   generateGraphParameters(graphData, selectedModel); 
  // });

  $("#models").on('input', function () {
    selectedModel = $('#models').val();
    generateGraphParameters(graphData, selectedModel); 
  });

  //prevent page reload on form send
  $("form").on("submit", function (e) {
    e.preventDefault();
  });
});

//collects all the parameters selected by the user,
//generates a json and sends to the server
function fetchParametersAndGetGraph(){
  //show loader animation
  $("#loader").show();

    //get the parameters
    //var modelParamJson = graphData.models[selectedModel];
    var modelParamJson = $.extend( true, {}, graphData.models[selectedModel] );

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
      }
    });
    //compile parameter json
    var json = {};
    json[selectedModel] = modelParamJson;

    //send to server to generate graph
    $.ajax({
        type: "POST",
        url: "/plot",
        success: displayGraph,
        error: serverErrorHandler,
        contentType:'application/json',
        data: JSON.stringify(json),
        dataType:'json'
      });
}

//display the graph received from the server
function displayGraph(data){
  //hide error message (if present)
  $("#err-msg").addClass("hidden");
  $("#graph-display").empty();

  var div = data.div;
  var js = data.js;

  console.log(div);
  console.log(js);

  $("#graph-display").append(div);
  $.getScript(js); 
  //switch to graph display tab
  $('.nav-pills a[href="#graph-display"]').tab('show');
  //hide loader animation
  $("#loader").hide();
}

//displays an error message
function serverErrorHandler(data){
  $('#err-msg').append(data);
  $('#loader').hide();
  $("#err-msg").show();
}

// //receives a json list of parameters and puts them in the x/y/machines parameters list
// function fillProjectParameters(data){
//   //hide error message (if present)
//   $("#err-msg").hide();
//   //save types info
//   var x = $("#x-axis").val();
//   var y = $("#y-axis").val();
//   var machine = $("#machines").val();
//   //delete previous options information
//   $("#x-axis").empty();
//   $("#y-axis").empty();
//   $("#machines").empty();

//   //fill parameter options
//   $.each(data.cols, function(i, value) {
//     $('#x-axis').append($('<option>').text(value).attr('value', value));
//     $('#y-axis').append($('<option>').text(value).attr('value', value));
//   });
//   $.each(data.machines, function(i,value){
//     $("#machines").append($("<option>").text(value).attr("value",value));
//   })

//   if(x != ""){
//     $("#x-axis").val(x);
//   }
//   if( y != ""){
//     $("#y-axis").val(y);
//   }
//   if( machine != ""){
//     $("#machines").val(machine);
//   }

//   $('.nav-pills a[href="#parameter-selection"]').tab('show');

//   $("#param-select").removeClass('disabled');
//   $('#loader').hide();
// }

//fills the model list
function handleParameters(data){
  graphData = data;

  fillModelList(data.models);
  $('.nav-pills a[href="#graph-selection"]').tab('show');
  $('#model-select').removeClass('disabled');
  $('#loader').hide();
}


//fill model list with all available models
function fillModelList(data){
  var modelsList = Object.keys(data);

  $.each(modelsList, function(i,value){
    var newOption = document.createElement("option");
    newOption.innerHTML = value;
    $('#models').append(newOption);
  });

  selectedModel = $('#models').val();
  generateGraphParameters(graphData, selectedModel);
}

//generates the required graph parameters
function generateGraphParameters(data, model){
  $('#parameter-selection').empty();
  var newP = document.createElement("p");
  newP.innerHTML = "Select graph parameters:";
  $('#parameter-selection').append(newP);

  //go over all the model parameters, generate an input field and fill in the input parameters
  $.each(data.models[model], function(key,value){
    var label = generateLabel(key,'col-xs-2 col-form-label',key);
    var input = generateInputField(key,value.type,data[value.source]);

    var formDiv = wrapInDiv([label,input],'form-group row');

    $('#parameter-selection').append(formDiv);
  });

  var submitButton = generateButton('param-select','btn','OK');
  $('#parameter-selection').append(submitButton);

  //handles parameter selection
  $('#param-select').on('click', fetchParametersAndGetGraph);
}

//generates a label
function generateLabel(forName,className,value){
  var newLabel = document.createElement("label");
  newLabel.innerHTML = value;
  newLabel.setAttribute("for",forName);
  newLabel.setAttribute("class",className);

  return newLabel;
}

//generates the required input element
function generateInputField(id,value,parameters){
  var newInput;
  switch(value){
    case 'single':
      newInput = generateDatalist(id);
      newInput[1] = fillListParameters(newInput[1],parameters);
      break;
    case 'multiple':
      newInput = generateSelect(id,true);
      newInput[0] = fillListParameters(newInput[0],parameters);
      break;
  }

  newInput = wrapInDiv(newInput, 'col-xs-10');
  return newInput;
}


//generates an array with an input and datalist elements in it
function generateDatalist(id){
  var newInput = document.createElement('input');
  newInput.setAttribute('class','form-control');
  newInput.setAttribute('list',id);
  newInput.setAttribute('id','input-'+id);

  var newDatalist = document.createElement('datalist');
  newDatalist.setAttribute('id',id);

  return [newInput,newDatalist];
}


//generates an array with a select element in it
function generateSelect(id,isMultiple){

  var newSelect = document.createElement('select');
  newSelect.setAttribute('id','input-'+id);
  newSelect.setAttribute('class','form-control');
  newSelect.multiple = isMultiple;

  return [newSelect];
}

//creates options from the given parameters and appends them to the given list element
function fillListParameters(element, parameters){
  //empty the given list
  $(element).empty();
  //fill with given parameters
  $.each(parameters, function(i,value){
    var newOption = document.createElement("option");
     newOption.innerHTML = value;
    element.append(newOption);
  });

  return element;
}

//receives an array of elements,
//wraps them in a div with 'className' and returns the div
function wrapInDiv(elements, className){
  var newDiv = document.createElement("div");
  newDiv.setAttribute('class',className);

  $.each(elements, function(i,value){
    newDiv.append(value);
  })

  return newDiv;
}

//generates a button with the required id and class
function generateButton(id,className,text){
  var newButton = document.createElement('button');
  newButton.setAttribute('id',id);
  newButton.setAttribute('class',className);
  newButton.innerHTML = text;

  return newButton;
}

//fixes the height of the graph display tab
function fixHeight(){
  remaining_height = parseInt($(window).height() - 250); 
  $('#graph-display').height(remaining_height); 
}

