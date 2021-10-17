console.log(solution_analysis)

var date_sub_elem = document.getElementById('date_sub')
var runtime_elem = document.getElementById('runtime_direct')
var time_comp_elem = document.getElementById('time_comp')
var score_elem = document.getElementById('score')
var solution_text_elem = document.getElementById('solution_text')


date_sub_elem.innerHTML = "Date Submitted: " + date_sub
var rt_message = solution_analysis["time_profile"]?  solution_analysis["udef_func_time_tot"]: "Time profiling has not been configured for this problem"
runtime_elem.innerHTML = "Runtime of " + capitalize(username) + "'s submission: " + rt_message
var comparator = solution_analysis["udef_func_time_tot"]/solution_analysis["ref_time"] >= 1? "slower": "faster";
var comp_msg = solution_analysis["time_profile"]? capitalize(username) + "'s submission was " + comparator + "than the reference problem by a fraction of " + solution_analysis["udef_func_time_tot"]/solution_analysis["ref_time"] + "s": "";
time_comp_elem.innerHTML = comp_msg
var score_color = solution_analysis["passed"]? "#06D6A0": "rgb(240, 79, 79)";
score_elem.style.color = score_color
score_elem.innerHTML = "Score: " + solution_analysis["score"] + "%"
var soln_text = solution_analysis["solution_text"]
for(let i = 0; i < soln_text.length; i++) {
    solution_text_elem.innerHTML += "<span style='white-space:pre;'>" + soln_text[i].italics() + "</span><br>"
}


function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
  