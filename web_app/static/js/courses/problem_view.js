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
var pseudo_section = document.getElementById('pseudocode')
console.log(solution_analysis)
var cprof_message = solution_analysis["time_profile"]?  (solution_analysis["udef_func_time_tot"]).toFixed(3) + "s (vs. " + (solution_analysis["ref_time"]).toFixed(3) + "s for reference problem)": "Time profiling has not been configured for this problem"
cprof_elem.innerHTML = "Runtime of " + html_username + "submission: " + cprof_message + "<br><br>"
var memprof_message = solution_analysis["total_physical_mem"] + "MiB (vs. " + solution_analysis["ref_phys_mem"] + "MiB for reference problem)"
memprof_elem.innerHTML = "Memory Usage of " + html_username + "submission: " + memprof_message
var score_color = solution_analysis["passed"]? "#06D6A0": "rgb(240, 79, 79)";
score_elem.style.color = score_color
score_elem.innerHTML = "Score: " + parseFloat(solution_analysis["score"]).toFixed(2) + "%"
var soln_text = solution_analysis["solution_text"]
solution_text_elem.innerHTML = "<h4><u>Solution Text:</u></h4><br>"
for(let i = 0; i < soln_text.length; i++) {
    solution_text_elem.innerHTML += "<span style='white-space:pre;'>" + soln_text[i].italics() + "</span><br>"
}
var pseudocode = solution_analysis["samp_skels"][0]

pseudo_section.innerHTML = "<h4><u>Reference Pseudocode:</u></h4><br>"
for(let i = 0; i < pseudocode.length; i++) {
    pseudo_section.innerHTML += "<span style='white-space:pre;'>" + pseudocode[i].italics() + "</span><br>"
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
        var scores = solution_analysis["scores"]
        var lim = Object.keys(scores).length
        for(var i = 1; i < lim; i++) {
            output_review_dd.innerHTML += "<li><a name='test_link' id='tl_" + i + "' class='dropdown-item' data-toggle='modal' data-target='#exampleModalCenter'>Test " + i + "</a></li>"
        }

        var test_links = document.getElementsByName("test_link")

        for(var i = 0; i < test_links.length; i++) {
            var test_link = document.getElementById("tl_" + (i + 1))
            test_link.addEventListener("click", write_modal_body.bind(e, (i+1)))
            
            test_link.style.color = solution_analysis["scores"]["test_" + (i+1)]["status"] == "success"? "#06D6A0": "rgb(240, 79, 79)";
        }

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
                        ; // implement?
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

function write_modal_body(test_idx) {
    var test_dict = solution_analysis["scores"]["test_" + test_idx]
    var detailed_stats = test_dict["detailed_stats"]
    var modal_body = document.getElementById("modal_body")
    var output_type_btn = document.getElementById("output_type_btn")
    var modal_title = document.getElementById("modal_title")
    
    if(detailed_stats["one-to-one"]) {
        handle_one_to_one(detailed_stats, role)
        var e = undefined
        output_type_btn.addEventListener("click", handle_one_to_one.bind(e, detailed_stats, role))
    }
    else {
        output_type_btn.style.visibility = "hidden"
        modal_title.innerHTML = "I/O Review:"
        modal_body.innerHTML = ""
        if(detailed_stats["submitter_visible"] || role == "tutor") {
            var color = test_dict["status"] == "success"? "#06D6A0": "rgb(240, 79, 79)";
            modal_body.innerHTML += "<h5 style='color:white;'><u>Input (" + detailed_stats["input"].length + " element" + add_s(detailed_stats["input"]) + ")"  + "</u>: </h5><p style='color:white;'>[" + detailed_stats["input"].join(", ") + "]</p>"
            modal_body.innerHTML += "<h5 style='color:white;'><u>Reference Output (" + detailed_stats["reference_output"].length + " element" + add_s(detailed_stats["reference_output"]) + ")" + "</u>: </h5><p style='color:#06D6A0;'>[" + detailed_stats["reference_output"].join(", ") + "]</p>"
            modal_body.innerHTML += "<h5 style='color:white;'><u>Your Output (" + detailed_stats["user_output"].length + " element" + add_s(detailed_stats["user_output"]) + ")" + "</u>: </h5><p style='color:" + color + ";'>[" + detailed_stats["user_output"].join(", ") + "]</p>"

        }
        else {
            modal_body.innerHTML += "<h3 style='color:white;'>Unavailable</h3>"
        }
    }
}

function add_s(array) {
    var append_string = array.length == 1? "": "s";
    return append_string
}

function gen_comp_string(comp_elem) {
    var table_string = ""
    table_string += "<thead><tr style='width:100%;text-align:center;padding:5 5 5 5;'>"
    table_string += "<th style='text-align:center;padding:5 5 5 5;' scope='col'><u>Input</u></th><th style='text-align:center;padding:5 5 5 5;' scope='col'><u>" + capitalize(submitter_name) + "'s Output</u></th><th style='text-align:center;padding:5 5 5 5;' scope='col'><u>Reference Output</u></th>"
    table_string += "</tr></thead><tbody>"

    for(var mm_index = 0; mm_index < comp_elem.length; mm_index++) {
        var bg_color = mm_index % 2 == 0? '#101010': 'rgb(55, 55, 55)';
        table_string += "<tr style='width:100%;text-align:center;padding:7 7 7 7;background-color:" + bg_color +";'><td style='padding: 7 7 7 7'><span style='color:white;'>" + comp_elem[mm_index][0] + "</span></td><td  style='padding: 5 5 5 5'><span style='color:rgb(240, 79, 79)'>" + comp_elem[mm_index][1] + "</span></td><td  style='padding: 5 5 5 5'><span style='color:#06D6A0'>" + comp_elem[mm_index][2] + "</span></td></tr>"
    }

    table_string += "</tbody>"
    return table_string
}

function handle_one_to_one(detailed_stats, role) {
    var modal_table = document.getElementById("modal_table")
    modal_table.innerHTML = ""
    var correct_or_incorrect = output_type_btn.value == 1? " Correct Outputs": " Incorrect Outputs";
    output_type_btn.innerHTML = output_type_btn.value == 1? "View Incorrect Outputs": "View Correct Outputs";
    var comp_key = output_type_btn.value == 1? "matches": "mismatches";
    var comp_elem = role == "tutor"? detailed_stats["total_" + comp_key]: detailed_stats[comp_key];
    var title_message = role == "student"? "Output Review: A Sample of " + comp_elem.length + correct_or_incorrect: "Output Review: " + comp_elem.length + correct_or_incorrect;
    modal_title.innerHTML = title_message
    modal_table.innerHTML = ""
    modal_table.innerHTML += gen_comp_string(comp_elem)
    output_type_btn.value = output_type_btn.value == 1? 0: 1;
}