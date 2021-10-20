var retrieve_stats_url = "http://localhost:8000/api/courses/get_global_problem_stats" // /<int:problem_id>/<int:course_id>/"
console.log(solution_analysis)
console.log(valid_student)

window.init_fetch = true
var data_obj;

var ctx = document.getElementById('myChart').getContext('2d');
if(ctx != null) {
    ctx.canvas.width = 700;
    ctx.canvas.height = 500;
}

var date_sub_elem = document.getElementById('date_sub')
var cprof_elem = document.getElementById('cprof')
var memprof_elem = document.getElementById('memprof')
var score_elem = document.getElementById('score')
var solution_text_elem = document.getElementById('solution_text')


date_sub_elem.innerHTML = "Date Submitted: " + date_sub
var cprof_message = solution_analysis["time_profile"]?  (solution_analysis["udef_func_time_tot"]).toFixed(3) + "s (vs. " + (solution_analysis["ref_time"]).toFixed(3) + "s for reference problem)": "Time profiling has not been configured for this problem"
cprof_elem.innerHTML = "Runtime of " + submitter_name + "'s submission: " + cprof_message
// var comparator = solution_analysis["udef_func_time_tot"]/solution_analysis["ref_time"] >= 1? "slower": "faster";
// var comp_msg = solution_analysis["time_profile"]? capitalize(username) + "'s submission was " + comparator + " than the reference problem by a fraction of " + (solution_analysis["udef_func_time_tot"]/solution_analysis["ref_time"]).toFixed(2): "";
// time_comp_elem.innerHTML = comp_msg
var memprof_message = solution_analysis["total_physical_mem"] + "MiB (vs. " + solution_analysis["ref_phys_mem"] + "MiB for reference problem)"
memprof_elem.innerHTML = "Memory Usage of " + submitter_name + "'s submission: " + memprof_message
var score_color = solution_analysis["passed"]? "#06D6A0": "rgb(240, 79, 79)";
score_elem.style.color = score_color
score_elem.innerHTML = "Score: " + solution_analysis["score"] + "%"
var soln_text = solution_analysis["solution_text"]
for(let i = 0; i < soln_text.length; i++) {
    solution_text_elem.innerHTML += "<span style='white-space:pre;'>" + soln_text[i].italics() + "</span><br>"
}

var stat_btn = document.getElementById('stat_btn')

if((role == "tutor" && valid_tutor) || (role == "student" && valid_student)) {
    fetch(retrieve_stats_url + "/" + problem_id + "/" + course_id + "/" + role + "/") 
            .then(response => response.json())
            .then(function (data) {
                data_obj = data
                stat_btn.addEventListener("click", function(e) {
                    if(role == "tutor") {
                        display_barchart(data_obj)
                    }
                    else {
                        ;
                    }
            })

        })
    }

// else if(role == "student" && valid_student) {
//     console.log("Hello student!")
    // stat_btn.addEventListener("click", function(e) {
    //     if(window.init_fetch) {
    //         fetch(retrieve_stats_url + "/" + problem_id + "/" + course_id + "/") 
    //         .then(response => response.json())
    //         .then(function (data) {
    //             data_obj = data
    //             data_array = []
    //             spot_color_array = []
    //             var unames = []
    //             for(let i = 0; i < data.length; i++) {
    //                 var gtime = data[i][0]
    //                 var gscore = data[i][1]
    //                 var gusername = data[i][2]
    //                 data_array.push({
    //                     x: gtime,
    //                     y: gscore
    //                 })
    //                 var spot_color = gscore >= solution_analysis["pass_threshold"]? "#06D6A0": "rgb(240, 79, 79)";
    //                 spot_color_array.push(spot_color)
    //                 unames.push(gusername)
    //             }
    //             console.log(data_array)
    //             display_scatterplot(data_array, unames)
    //             window.init_fetch = false
    //         })
    // }
    // else {
    //     console.log(data_obj)
    // }
    // })
// }

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
  
function display_scatterplot(data_obj) {
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

function display_barchart(data_obj) {
    try {
        window.chart.destroy();
    }
    catch (err) {
        ;
    }

    var labels = []
    var scores = []
    var colors = [] 
    var borderColors = []
    for(let i = 0; i < data_obj.length; i++) {
        student_dict = data_obj[i]
        labels.push(student_dict["username"])
        scores.push(student_dict["score"])
        var borderC = student_dict["username"] == submitter_name? "gold": "";
        borderColors.push(borderC)
        var bgColor = student_dict["score"] >= solution_analysis["pass_threshold"]? "green": "red";
        colors.push(bgColor)
    }
    var dataset = [
        {
            label: "Score (%)",
            data: scores,
            backgroundColor: colors,
            borderColor: borderColors,
            borderWidth: 2
        },
    ];

    var options = {
        maintainAspectRatio: false,
        responsive: true,
        scales: {
            xAxes: [{
                barPercentage: 0.4,
            },
            {
                scaleLabel: {
                    display: true,
                    labelString: 'Username'
                },
                ticks: {
                    min: 0,
                    display: false
                },
                stacked: true,
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '% Score',
                },
                ticks: {
                    min: 0
                },
                stacked: true,
            }]
        }
    };

    var content = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: dataset
        },
        options
    };

    window.chart = new Chart(ctx, content);
}