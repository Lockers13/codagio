const MAX_FILE_UPLOAD_SIZE = 100000

$("#prob_form").submit(function(e) {
    e.preventDefault();
    
    // checking uploaded file sizes are all under 100KB 

    function get_elem_if_any(name_str, elem_list) {
        try {
            var elem = document.getElementsByName(name_str)[0]
            elem_list.push(elem)
        }
        catch (err) {
            console.log(err)
        }
    }

    var input_elems =[]
    var name_str_list = ["program", "meta_file", "custom_inputs", "extra_input_files"]

    for(let index = 0; index < name_str_list.length; index++) {
        get_elem_if_any(name_str_list[index], input_elems)
    }

    var upload_files = []
    for(let k = 0; k < input_elems.length; k++) {
        try {
            var files = input_elems[k].files
            upload_files.push(files)
        }
        catch (err) {
            console.log(err)
        }
    }
    let error_p = document.getElementById("form_upload_error")
    error_p.innerHTML = ""
    for (let i = 0; i < upload_files.length; i++) {
        if(upload_files[i] != undefined) {
            for (let j = 0; j < upload_files[i].length; j++) {
                if(upload_files[i][j] != undefined && upload_files[i][j].size >= MAX_FILE_UPLOAD_SIZE) {
                    error_p.innerHTML += "Error - file: " + upload_files[i][j].name + " is too large!"
                    return
                }
            }
        }
    }

    // end of file size check

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