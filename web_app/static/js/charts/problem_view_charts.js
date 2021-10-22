function display_scatterplot(data_obj) {
    // document.getElementById("graph_heading").innerHTML = "<p style='margin:50px 0px 0px 0px;text-align:center'>Time spent in function => " + fdef["cum_time"] + " seconds</p>"
    try {
        window.chart.destroy();
    }
    catch (err) {
        ;
    }
    var tooltip_info = []
    var xy_data = []
    var colors = []
    var unames = []
    var borderColors = []
    for(let i = 0; i < data_obj.length; i++) {
        student_dict = data_obj[i]
        var uname = student_dict["username"] == submitter_name && data_obj["role"] == "student"? "You": "";
        unames.push(uname)
        var cprof = parseFloat(student_dict["tot_time"])
        var memprof = parseFloat(student_dict["tot_mem"])
        var tt_info_string = cprof + "s, " + memprof + "MiB"
        tooltip_info.push(tt_info_string)
        xy_data.push({
            x: cprof,
            y: memprof
        })
        var bgColor = student_dict["username"] == submitter_name && data_obj["role"] == "student"? "gold": "blue";
        colors.push(bgColor)
        var borderC = student_dict["score"] >= pass_threshold? "green": "red";
        borderColors.push(borderC)
    }
    var tooltipText = tooltip_info
    var dataset = [
        {
            label: "PerfStats",
            data: xy_data,
            backgroundColor: colors,
            borderColor: borderColors,
            pointRadius: 7,
            borderWidth: 3
        },
    ];

    var options = {
        maintainAspectRatio: false,
        scaleOptions: {
            ticks: {
                beginAtZero: true
            }
        },
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
                position: "bottom",
                min: 0
            },
            {
                scaleLabel: {
                    display: true,
                    labelString: 'RunTime (s)'
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
                    labelString: 'Memory Usage (MiB)',
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
            labels: unames,
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
        var uname = student_dict["username"] == submitter_name && data_obj["role"] == "student"? "You": "";
        labels.push(uname)
        scores.push(student_dict["score"])
        var bgColor = student_dict["username"] == submitter_name && data_obj["role"] == "student"? "gold": "blue";
        colors.push(bgColor)
        var borderC = student_dict["score"] >= pass_threshold? "green": "red";
        borderColors.push(borderC)
    }
    var dataset = [
        {
            label: "Score (%)",
            data: scores,
            backgroundColor: colors,
            borderColor: borderColors,
            borderWidth: 4,
            barPercentage: 0.1
        },
    ];

    var options = {
        maintainAspectRatio: false,
        responsive: true,
        scales: {
            xAxes: [{
               
            },
            {
                scaleLabel: {
                    display: true,
                    labelString: ''
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