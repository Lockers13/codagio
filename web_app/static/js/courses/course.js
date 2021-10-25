const create_course_url = "http://localhost:8000/api/courses/create_course/"
let course_landing_url = "http://localhost:8000/classes/course_landing/"
const enrol_course_url = "http://localhost:8000/api/courses/enrol_course/"
const get_course_url = "http://localhost:8000/api/courses/get_course/"

var enrol_form_btn = document.getElementById("enrol_form_btn")
var enrol_form_div = document.getElementById("enrol_form_div")
var cc_form_btn = document.getElementById("cc_form_btn")
var cc_form_div = document.getElementById("cc_form_div")
var effective_enrol = document.getElementById("effective_enrol")

$(document).ready(function(){
    enrol_form_div.style.visibility = "hidden"
})

var csearch_btn = document.getElementById("search_button")
var course_fetch_error = document.getElementById("course_fetch_error")
var course_info = document.getElementById("course_info")
var passcode_span = document.getElementById("passcode_span")

if(enrol_form_btn != null) {
    enrol_form_btn.addEventListener('click', function(e) {
        enrol_form_div.style.visibility = "visible"
        enrol_form_btn.style.visibility = "hidden"
        csearch_btn.addEventListener("click", function(e) {
            var course_code = document.getElementsByName("course_code")[0].firstChild.value
            ce_res.innerHTML = ""
            fetch(get_course_url + "?course_code=" + course_code) 
            .then(response => response.json())
            .then(function (data) {
                document.getElementById("passcode_entry_field").firstChild.value = ""
                try {
                    if(data.includes("no such course")) {
                        effective_enrol.style.visibility = "hidden"
                        course_fetch_error.innerHTML = "Sorry, we could not find that course...please try again!"
                        return
                    }
                }
                catch {
                    ;
                }
                course_fetch_error.innerHTML = ""
                passcode_span.innerHTML = "Enter Passcode for " + course_code + ":"
                course_info.innerHTML = ""
                // course_fetch_error.innerHTML = ""
                // course_info.innerHTML += "<div style='text-align:center;'><ul><li>Name: " + data["name"] + "</li><br>"
                // course_info.innerHTML += "<li>Description: \"<i>" + data["description"] + "<\i>\"</li><br>"
                // course_info.innerHTML += "<li>Tutor: " + data["tutor"] + "</li></ul></div><br>"
                effective_enrol.style.visibility = "visible"
                $("#enrol_course_form").submit(function(e) {
                    e.preventDefault();
                    var ce_res = document.getElementById("ce_res")
                    $.ajax({
                        url: enrol_course_url + course_code +"/",
                        type: 'POST',
                        headers: {
                            "X-CSRFToken": window.CSRF_TOKEN
                        },
                        data: new FormData(this),
                        processData: false,
                        contentType: false,
                    })
                    .done(function(resp_data) {
                        ce_res.innerHTML = ""
                        window.location.href = course_landing_url + resp_data // resp_data on success is course_id
                    })
                    .fail(function(resp_data) {
                        console.log(resp_data)
                        ce_res.style.color = "red"
                        ce_res.innerHTML = resp_data["responseJSON"]
                    })
                });
            })
        })
    }) 
}

if(cc_form_btn != null) {
    cc_form_btn.addEventListener('click', function(e) {
        cc_form_div.style.visibility = cc_form_btn.value == 0? "visible": "hidden";
        cc_form_btn.value = cc_form_btn.value == 0? 1: 0;
        cc_form_btn.innerHTML = cc_form_btn.value == 0? "Click here to create a new course": "Hide Course Creation Form";
    })
} 

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