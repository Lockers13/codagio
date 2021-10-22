var retrieve_stats_url = "http://localhost:8000/api/courses/get_global_problem_stats" // /<int:problem_id>/<int:course_id>/"

var stat_btn = document.getElementById('stat_btn')


window.init_fetch = true
window.tutor_chart_alt = 1

var data_obj;

var ctx = document.getElementById('myChart').getContext('2d');
if(ctx != null) {
    ctx.canvas.width = 700;
    ctx.canvas.height = 500;
}

if(valid_tutor) {
    fetch(retrieve_stats_url + "/" + problem_id + "/" + course_id + "/" + role + "/") 
            .then(response => response.json())
            .then(function (data) {
                data_obj = data
                data_obj["role"] = role
                stat_btn.addEventListener("click", function(e) {
                    if(window.tutor_chart_alt) {
                        display_barchart(data_obj)
                        window.tutor_chart_alt = 0
                        stat_btn.innerHTML = "View Performance Chart"
                    }
                    else {
                        display_scatterplot(data_obj)
                        window.tutor_chart_alt = 1
                        stat_btn.innerHTML = "View Score Chart"
                    }
            })

        })
    }