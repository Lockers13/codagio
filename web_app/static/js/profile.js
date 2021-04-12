
var toggle = document.getElementById("toggle")

toggle.addEventListener('click', toggle_display)

function toggle_display() {
    if(toggle.value == 0) {
        var solutions_div = document.getElementById("solutions_saved")
        var prob_upload_div = document.getElementById("problems_uploaded")
        var prof_right = document.getElementById("prof_right")
        var prof_right_hidden = document.getElementById("prof_right_hidden")
        solutions_div.style.visibility = "hidden"
        var current_right = prof_right.innerHTML
        prob_upload_div.style.visibility = "visible"
        prof_right.innerHTML = prof_right_hidden.innerHTML
        prof_right_hidden.innerHTML = current_right
        toggle.innerHTML = "View Your Saved Solutions"
        toggle.value = 1
    }
    else {
        var solutions_div = document.getElementById("solutions_saved")
        var prob_upload_div = document.getElementById("problems_uploaded")
        var prof_right = document.getElementById("prof_right")
        var prof_right_hidden = document.getElementById("prof_right_hidden")
        prob_upload_div.style.visibility = "hidden"
        var current_right = prof_right.innerHTML
        solutions_div.style.visibility = "visible"
        prof_right.innerHTML = prof_right_hidden.innerHTML
        prof_right_hidden.innerHTML = current_right
        toggle.innerHTML = "View Your Uploaded Problems"
        toggle.value = 0
    }
}
