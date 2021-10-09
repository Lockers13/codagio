const enrol_course_url = "http://localhost:8000/classes/enrol_course/"
let course_landing_url = "http://localhost:8000/classes/course_landing/"

$("#enrol_course_form").submit(function(e) {
    e.preventDefault();
    var ce_res = document.getElementById("ce_res")
    $.ajax({
        url: enrol_course_url,
        type: 'POST',
        headers: {
            "X-CSRFToken": window.CSRF_TOKEN
        },
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    .done(function(resp_data) {
        console.log(resp_data)
        window.location.href = course_landing_url + resp_data // resp_data on success is course_id
    })
    .fail(function(resp_data) {
        console.log(resp_data)
        ce_res.style.color = "red"
        ce_res.innerHTML = "Oops, there was an error uploading your file, please ensure everything is in order and try again!"
    })
});
