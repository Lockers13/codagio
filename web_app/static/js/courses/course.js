const create_course_url = "http://localhost:8000/api/courses/create_course/"
let course_landing_url = "http://localhost:8000/classes/course_landing/"
const enrol_course_url = "http://localhost:8000/api/courses/enrol_course/"

let enrol_form_btn = document.getElementById("enrol_form_btn")
let enrol_form_div = document.getElementById("enrol_form_div")
let cc_form_btn = document.getElementById("cc_form_btn")
let cc_form_div = document.getElementById("cc_form_div")

if(enrol_form_btn != null) {
    enrol_form_btn.addEventListener('click', function(e) {
        enrol_form_div.style.visibility = enrol_form_btn.value == 0? "visible": "hidden";
        enrol_form_btn.value = enrol_form_btn.value == 0? 1: 0;
        enrol_form_btn.innerHTML = enrol_form_btn.value == 0? "Click here to enrol in a new course": "Hide Enrolment Form";
    }) 
}

if(cc_form_btn != null) {
    cc_form_btn.addEventListener('click', function(e) {
        cc_form_div.style.visibility = cc_form_btn.value == 0? "visible": "hidden";
        cc_form_btn.value = cc_form_btn.value == 0? 1: 0;
        cc_form_btn.innerHTML = cc_form_btn.value == 0? "Click here to create a new course": "Hide Course Creation Form";
    })
} 

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
        window.location.href = course_landing_url + resp_data // resp_data on success is course_id
    })
    .fail(function(resp_data) {
        console.log(resp_data)
        cc_res.style.color = "red"
        cc_res.innerHTML = "Oops, there was an error uploading your file, please ensure everything is in order and try again!"
    })
});