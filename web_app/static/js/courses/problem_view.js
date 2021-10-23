var retrieve_stats_url = "http://localhost:8000/api/courses/get_global_problem_stats" // /<int:problem_id>/<int:course_id>/"

var stat_btn = document.getElementById('stat_btn')
if(role == "tutor" || !latest) {
    stat_btn.style.visibility = "hidden"
}
const pass_threshold = solution_analysis["pass_threshold"]


window.init_fetch = true
window.student_chart_alt = 1

var data_obj;
var html_username = role == "student"? "your ": submitter_name + "'s ";

var ctx = document.getElementById('myChart').getContext('2d');
if(ctx != null) {
    ctx.canvas.width = 700;
    ctx.canvas.height = 500;
}

var cprof_elem = document.getElementById('cprof')
var memprof_elem = document.getElementById('memprof')
var score_elem = document.getElementById('score')
var solution_text_elem = document.getElementById('solution_text')

var cprof_message = solution_analysis["time_profile"]?  (solution_analysis["udef_func_time_tot"]).toFixed(3) + "s (vs. " + (solution_analysis["ref_time"]).toFixed(3) + "s for reference problem)": "Time profiling has not been configured for this problem"
cprof_elem.innerHTML = "Runtime of " + html_username + "submission: " + cprof_message
var memprof_message = solution_analysis["total_physical_mem"] + "MiB (vs. " + solution_analysis["ref_phys_mem"] + "MiB for reference problem)"
memprof_elem.innerHTML = "Memory Usage of " + html_username + "submission: " + memprof_message
var score_color = solution_analysis["passed"]? "#06D6A0": "rgb(240, 79, 79)";
score_elem.style.color = score_color
score_elem.innerHTML = "Score: " + solution_analysis["score"] + "%"
var soln_text = solution_analysis["solution_text"]
for(let i = 0; i < soln_text.length; i++) {
    solution_text_elem.innerHTML += "<span style='white-space:pre;'>" + soln_text[i].italics() + "</span><br>"
}



if((role == "student" && valid_student)) {
    fetch(retrieve_stats_url + "/" + problem_id + "/" + course_id + "/" + role + "/") 
            .then(response => response.json())
            .then(function (data) {
                console.log(data)
                data_obj = data
                data_obj["role"] = role
                stat_btn.addEventListener("click", function(e) {
                    if(role == "student") {
                        if(window.student_chart_alt) {
                            display_barchart(data_obj)
                            window.student_chart_alt = 0
                            stat_btn.innerHTML = "View Performance Chart"
                        }
                        else {
                            display_scatterplot(data_obj)
                            window.student_chart_alt = 1
                            stat_btn.innerHTML = "View Score Chart"
                        }
                    }
                    else {
                        ;
                    }
            })

        })
    }


function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}