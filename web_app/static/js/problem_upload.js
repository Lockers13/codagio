$("#prob_form").submit(function(e) {
    e.preventDefault();
    $.ajax({
        url: 'http://localhost:8000/code/save_problem/',
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    .done(function(resp_data) {
        console.log(resp_data)
    })
    .fail(function(resp_data) {
        console.log(resp_data)
    })
});

$("#input_type_select").on('change', function() {
    let input_type = document.getElementsByName('input_type')[0].value
    let custom_input_div = document.getElementById("custom_input_div")
    if(input_type == 'Custom') {
        custom_input_div.innerHTML += "<span class='input_title'>Custom Input File (.json format): </span><input type='file' required name='custom_inputs' id='custom_inputs'>"
    }
    else if(input_type == 'Auto') {
        custom_input_div.innerHTML = ""
    }
  });