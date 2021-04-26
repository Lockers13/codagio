const MAX_FILE_UPLOAD_SIZE = 1000000
const problem_upload_url = "http://localhost:8000/api/code/save_problem/"

$("#prob_form").submit(function(e) {
    e.preventDefault();
    var upload_res = document.getElementById("form_upload_res")
    upload_res.innerHTML = ""
    
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
    var name_str_list = ["program", "meta_file", "custom_inputs", "target_file", "data_file"]

    for(let index = 0; index < name_str_list.length; index++) {
        get_elem_if_any(name_str_list[index], input_elems)
    }

    var upload_files = []
    for(let k = 0; k < input_elems.length; k++) {
        try {
            var files = input_elems[k].files
            if(files.length > 3) {
                alert("Sorry, only a maximum of 3 target files is allowed!")
                return
            }
            upload_files.push(files)
        }
        catch (err) {
            console.log(err)
        }
    }
    for (let i = 0; i < upload_files.length; i++) {
        if(upload_files[i] != undefined) {
            for (let j = 0; j < upload_files[i].length; j++) {
                if(upload_files[i][j] != undefined && upload_files[i][j].size >= MAX_FILE_UPLOAD_SIZE) {
                    upload_res.style.color = "red"
                    upload_res.innerHTML += "Error - file: " + upload_files[i][j].name + " is too large!"
                    return
                }
            }
        }
    }

    // end of file size check

    $.ajax({
        url: problem_upload_url,
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    .done(function(resp_data) {
        console.log(resp_data)
        upload_res.style.color = "green"
        upload_res.innerHTML = "Congrats, your problem was uploaded successfully!"
    })
    .fail(function(resp_data) {
        console.log(resp_data)
        upload_res.style.color = "red"
        upload_res.innerHTML = "Oops, there was an error uploading your file, please ensure everything is in order and try again!"
    })
});
