let delete_base_url = "http://localhost:8000/api/courses/delete/course/"
let delete_response_url = "http://localhost:8000/classes/delete_response/course/"

var confirm_deactivate = document.getElementById("confirm_deactivate")
confirm_deactivate.onclick = handle_decision

function handle_decision(e) {
    var target_id = e.target.id
    if (target_id == "confirm") {
        var deactivation_response = document.getElementById("deactivation_response")
        $.ajax({
            url: delete_base_url + window.course_id + "/",
            method: "POST",
            headers: { 'X-CSRFToken': window.csrf_token },
        }).done(function (response) {
            window.location.href = delete_response_url + window.course_id + "/"
        }).fail(function (error) {
            deactivation_response.innerHTML = "<p style='color:red'>Uh oh, there was an error deactivating your course!</p>"
        });
    }
}
