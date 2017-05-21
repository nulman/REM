// @edited: Liran Funaro <funaro@cs.technion.ac.il>
// @author: Hadas Shahar <hshaha05@campus.haifa.ac.il>

///////////holds all the Graph Generation functions///////////////////////

///global variables:

var presets;           //holds the presets received from the server

///on document ready:

$(document).ready(function() {
  try{

  //add listener to preset select button
  $('#preset-list').change(function(){
    $('#select-preset').removeClass('disabled');
    $('#delete-preset').removeClass('disabled');
  });

  //add listener to preset select button
  $('#select-preset').click(selectPreset);
  $('#preset-list').dblclick(selectPreset);

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
    //clear input and hide save as dialog
    $('#preset-name').val('');
    $('#save-as-wrapper').hide();

    //get all other preset parameters and send to server
    var presetParameters = fetchFormParameters();
    //send save command to the sever and then refresh the preset list
    savePreset(presetName, presetParameters)
  });

  $('#delete-preset').click(function(){
    var presetName = selectedPresetName();
    deletePresets([presetName])
  });

  $('#reload-preset').click(updatePresetList);

  }catch(e){
  $("#notification").html(e.message);
}
});


///functions:

function deletePresets(presets) {
  $.when(
    asyncDeletePreset(presets, displayOkMessage, serverErrorHandler)
  ).then(updatePresetList);
}

function savePreset(name, parameters) {
  $.when(
    asyncSavePreset(name, parameters, displayOkMessage, serverErrorHandler)
  ).then(updatePresetList);
}

function selectedPresetName() {
  var selectedPreset = $('#preset-list').val();
  var reg = /^(.*)\:\s{6}/g;
  return reg.exec(selectedPreset)[1];
}

function selectPreset() {
  $('#loader').show();
  var presetName = selectedPresetName();

  if(presetName != null){
    sendPlotRequest(presets[presetName]);
  }else{
    $('#notification').html("couldn't parse preset name out of selected preset");
  }
}

//requests the preset list from the server - used to fill the 'load' section
function updatePresetList() {
  asyncLoadPresets(selectedFile, function (data){
    //fills the preset list with the response from the server
    presets = data;
    var result = [];

    //will display the name, followed by spaces, and the preset values
    for (var key in data) {
      result.push(key +":\xa0\xa0\xa0\xa0\xa0\xa0\xa0" + JSON.stringify(data[key])+"'");
    }

    fillListParameters($('#preset-list'), result);
  });
}
