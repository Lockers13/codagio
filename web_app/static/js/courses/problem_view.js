var retrieve_stats_url = "http://localhost:8000/api/courses/get_global_problem_stats" // /<int:problem_id>/<int:course_id>/"
console.log(solution_analysis)
console.log(valid_student)


var ctx = document.getElementById('myChart').getContext('2d');
if(ctx != null) {
    ctx.canvas.width = 700;
    ctx.canvas.height = 500;
}

var date_sub_elem = document.getElementById('date_sub')
var runtime_elem = document.getElementById('runtime_direct')
var time_comp_elem = document.getElementById('time_comp')
var score_elem = document.getElementById('score')
var solution_text_elem = document.getElementById('solution_text')


date_sub_elem.innerHTML = "Date Submitted: " + date_sub
var rt_message = solution_analysis["time_profile"]?  (solution_analysis["udef_func_time_tot"]).toFixed(2) + "s": "Time profiling has not been configured for this problem"
runtime_elem.innerHTML = "Runtime of " + capitalize(username) + "'s submission: " + rt_message
var comparator = solution_analysis["udef_func_time_tot"]/solution_analysis["ref_time"] >= 1? "slower": "faster";
var comp_msg = solution_analysis["time_profile"]? capitalize(username) + "'s submission was " + comparator + " than the reference problem by a fraction of " + (solution_analysis["udef_func_time_tot"]/solution_analysis["ref_time"]).toFixed(2): "";
time_comp_elem.innerHTML = comp_msg
var score_color = solution_analysis["passed"]? "#06D6A0": "rgb(240, 79, 79)";
score_elem.style.color = score_color
score_elem.innerHTML = "Score: " + solution_analysis["score"] + "%"
var soln_text = solution_analysis["solution_text"]
for(let i = 0; i < soln_text.length; i++) {
    solution_text_elem.innerHTML += "<span style='white-space:pre;'>" + soln_text[i].italics() + "</span><br>"
}

if(valid_student) {
    var stat_btn = document.getElementById('stat_btn')
    stat_btn.addEventListener("click", function(e) {
        fetch(retrieve_stats_url + "/" + problem_id + "/" + course_id + "/") 
        .then(response => response.json())
        .then(function (data) {
            data_array = []
            spot_color_array = []
            var unames = []
            for(let i = 0; i < data.length; i++) {
                var gtime = data[i][0]
                var gscore = data[i][1]
                var gusername = data[i][2]
                data_array.push({
                    x: gtime,
                    y: gscore
                })
                var spot_color = gscore >= solution_analysis["pass_threshold"]? "#06D6A0": "rgb(240, 79, 79)";
                spot_color_array.push(spot_color)
                unames.push(gusername)
            }
            console.log(data_array)
            display_scatterplot(data_array, unames)
        })
    })
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
  
function display_scatterplot(data_array, unames) {
    // document.getElementById("graph_heading").innerHTML = "<p style='margin:50px 0px 0px 0px;text-align:center'>Time spent in function => " + fdef["cum_time"] + " seconds</p>"
    try {
        window.chart.destroy();
    }
    catch (err) {
        ;
    }

    var labels = []
    var tooltipText = unames
    var dataset = [
        {
            label: "%",
            data: data_array,
            backgroundColor: spot_color_array,
            pointRadius: 10
        },
    ];

    var options = {
        maintainAspectRatio: false,
        tooltips: {
            callbacks: {
                  title: function(tooltipItem, data) {
                    var title = tooltipText[tooltipItem[0].index];
                    return title;
                  },
                  label: function(tooltipItem, data) {
                    return data.labels[tooltipItem.index];
                  }
                }
        },
        responsive: false,
        scales: {
            xAxes: [{
                type: "linear",
                position: "bottom"
            },
            {
                scaleLabel: {
                    display: true,
                    labelString: '%'
                },
                ticks: {
                    min: 0
                },
                stacked: true,
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '#',
                },
                ticks: {
                    min: 0
                },
                stacked: true,
            }]
        }
    };

    var content = {
        type: 'scatter',
        data: {
            labels: labels,
            datasets: dataset
        },
        options
    };

    window.chart = new Chart(ctx, content);
}