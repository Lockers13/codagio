const create_course_url = "http://localhost:8000/classes/create_course/"

$("#create_course_form").submit(function(e) {
    e.preventDefault();
    var cc_res = document.getElementById("cc_res")
    $.ajax({
        url: create_course_url,
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    .done(function(resp_data) {
        console.log(resp_data)
        cc_res.style.color = "green"
        cc_res.innerHTML = "Congrats, your problem was uploaded successfully!"
    })
    .fail(function(resp_data) {
        console.log(resp_data)
        cc_res.style.color = "red"
        cc_res.innerHTML = "Oops, there was an error uploading your file, please ensure everything is in order and try again!"
    })
});
