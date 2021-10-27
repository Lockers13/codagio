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
cprof_elem.innerHTML = "Runtime of " + html_username + "submission: " + cprof_message + "<br><br>"
var memprof_message = solution_analysis["total_physical_mem"] + "MiB (vs. " + solution_analysis["ref_phys_mem"] + "MiB for reference problem)"
memprof_elem.innerHTML = "Memory Usage of " + html_username + "submission: " + memprof_message
var score_color = solution_analysis["passed"]? "#06D6A0": "rgb(240, 79, 79)";
score_elem.style.color = score_color
score_elem.innerHTML = "Score: " + solution_analysis["score"] + "%"
var soln_text = solution_analysis["solution_text"]
for(let i = 0; i < soln_text.length; i++) {
    solution_text_elem.innerHTML += "<span style='white-space:pre;'>" + soln_text[i].italics() + "</span><br>"
}

var content_str = "<ul>"
var fdefs = solution_analysis["fdefs"]
for(fdef in fdefs) {
    var cumulative_time = solution_analysis["time_profile"] == true? fdefs[fdef]["cum_time"]: "Time profiling has not been configured for this problem!"
    content_str += "<li>Function Name: " + fdefs[fdef]["name"] + "<br>" +
                    "Cumulative Time spent in function: " + cumulative_time+ "</li><br>"
}
content_str += "</ul>"
cprof_elem.innerHTML += content_str

var output_review = document.getElementById("output_review")
var output_review_dd = document.getElementById("output_review_dd")


if(output_review != null) {
    output_review.addEventListener('click', function(e) {
        e.preventDefault()
        output_review_dd.innerHTML = ""
        console.log(solution_analysis)
        var scores = solution_analysis["scores"]
        var lim = Object.keys(scores).length
        for(var i = 1; i < lim; i++) {
            output_review_dd.innerHTML += "<li><a id='review_test_" + i + "' class='dropdown-item' data-toggle='modal' data-target='#exampleModalCenter'>Test " + i + "</a></li>"
            document.getElementById("review_test_" + i).addEventListener('click', write_modal_body.bind(e, i))
        }

        // handle_output_analysis()
    })
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

function handle_output_analysis(e) {
    var modal_body = document.getElementById("modal_body")
    modal_body.innerHTML = "HEY YOU!"
    console.log(solution_analysis)
}

function write_modal_body(test_idx, e) {
    // not sure why but JS engine is inverting the order of event and test_idx when passed in bind method
    var modal_title = document.getElementById("modal_title")
    var modal_table = document.getElementById("modal_table")
    modal_table.innerHTML = ""
    modal_table.innerHTML += "<thead><tr style='width:100%;text-align:center;padding:5 5 5 5;'>"
    modal_table.innerHTML += "<th style='text-align:center;padding:5 5 5 5;' scope='col'><u>" + capitalize(submitter_name) + "'s Output</u></th><th style='text-align:center;padding:5 5 5 5;' scope='col'><u>Correct Solution</u></th>"
    modal_table.innerHTML += "</tr></thead><tbody>"
    var mismatches = solution_analysis["scores"]["test_" + test_idx]["detailed_stats"]["total_mismatches"]
    modal_title.innerHTML = mismatches.length + " Incorrect Outputs"
    for(var mm_index = 0; mm_index < mismatches.length; mm_index++) {
        var bg_color = mm_index % 2 == 0? '#101010': 'rgb(55, 55, 55)';
        modal_table.innerHTML += "<tr style='width:100%;text-align:center;padding:7 7 7 7;background-color:" + bg_color +";'><td style='padding: 7 7 7 7'><span style='color:rgb(240, 79, 79)'>" + mismatches[mm_index][0] + "</span></td>" + "<td  style='padding: 5 5 5 5'><span style='color:#06D6A0'>" + mismatches[mm_index][1] + "</span></td></tr>"
    }
    modal_table.innerHTML += "</tbody>"
}
