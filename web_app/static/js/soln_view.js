const analysis_view_url = "http://localhost:8000/code/analysis/"
const func_line_offset = 3

var ctx = document.getElementById('myChart').getContext('2d');
ctx.canvas.width = 700;
ctx.canvas.height = 500;

var container_header =  document.getElementById("container_header")
var overview_stats_div = document.getElementById("overview_stats")
var detailed_stats_div = document.getElementById("detailed_stats")

fetch(analysis_view_url + soln_id) 
.then(response => response.json())
.then(function (data) {
    container_header.innerHTML = data["problem__name"]
    console.log(data)
    var analysis = data["analysis"]
    var soln_text = analysis["solution_text"]
    overview_stats_div.innerHTML += "<div id='soln_code'><p>"
    for(let i = 0; i < soln_text.length; i++) {
        overview_stats_div.innerHTML += "<span name='codeline' id='codeline_" + (i+1) + "' style='font-style: italic;'>" + (i+1) + "." + "&nbsp&nbsp&nbsp&nbsp" + soln_text[i].replace(/\s/g, '&nbsp') + "</span><br>"
    }
    overview_stats_div.innerHTML += "</p></div>"
    var ref_time = parseFloat(analysis["ref_time"])
    var soln_time = parseFloat(analysis["udef_func_time_tot"])
    overview_stats_div.innerHTML += "<div><br><br>"
    overview_stats_div.innerHTML += "<p>Your computation time: " + soln_time + "</p>"
    overview_stats_div.innerHTML += "<p>Time taken by reference problem: " + ref_time + "</p>"
    var comp_str = ""
    if(!(soln_time == ref_time)) {
        comp_str += "Looks like you were "
        comp_str += soln_time > ref_time? "slower": "faster"
        comp_str += " than the reference problem by a fraction of "
        comp_str += Math.round((soln_time > ref_time ? soln_time/ref_time: ref_time/soln_time) * 100) / 100
    }
    else
        comp_str += "Looks like your solution took more or less the same time to execute as the uploaded reference problem"
    overview_stats_div.innerHTML += "<p>" + comp_str + "</p>"
    overview_stats_div.innerHTML += "<br><br><div id='lprof_btn_div' class='d-flex justify-content-left'></div></div>"
    var fdefs = analysis["fdefs"]
    var lprof_str = ""
    write_lprof(lprof_btn_div, fdefs, lprof_str)
    bind_lprof_btns(fdefs)
})

function display_lp_graph(fdef) {
   // document.getElementById("graph_heading").innerHTML = "<p style='margin:50px 0px 0px 0px;text-align:center'>Time spent in function => " + fdef["cum_time"] + " seconds</p>"
    try {
        window.chart.destroy();
    }
    catch(err) {
        ;
    }
    console.log(fdef)
    var lprof_dict = fdef["line_profile"]
    var percentage_times = []
    var line_nos = []

    for(line in lprof_dict) {
        try{
            var p_time = parseFloat(lprof_dict[line]["%time"])
            percentage_times.push(p_time)
        }
        catch(err) {
            percentage_times.push(0.0)
        }
        var line_num = parseInt(line.split("_")[1])
        line_nos.push(line_num - func_line_offset)
    }

    var labels = line_nos
    var dataset = [
        {   
            label: "% of function time spent executing line",
            data: percentage_times,
            backgroundColor: "#1d2b5b"
        },
    ];

    var options = {
        onHover: function (e) {
            try {
                var activePointLabel = this.getElementsAtEvent(e)[0]._model.label;
                var codelines = document.getElementsByName("codeline")
                for(let i = 0; i < codelines.length; i++) {
                    codelines[i].style.color = "white"
                }
                var codeline = document.getElementById("codeline_" + activePointLabel)
                var pc_time = percentage_times[parseInt(activePointLabel)-1]
                let color_val = pc_time < 66.6 ? ((pc_time < 33.3)? "#06D6A0": "orange"): "red";
                codeline.style.color = color_val
            }
            catch(err) {
                ;
            }
        },
        maintainAspectRatio : false,
        responsive: false,
        scales: {
            xAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '% Time'
                },
                stacked: true,
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: 'Line No.',
                },
                ticks: {
                    max : line_nos[line_nos.length - 1],
                    min : line_nos[0],
                },
                stacked: true,
            }]
        }
    };

    var content = {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: dataset
        },
        options
    };

    window.chart = new Chart(ctx, content);
    console.log(window.chart)
}

function write_lprof(div, fdefs, lprof_str) {
    div.innerHTML = ""
    lprof_str += "<div style='text-align:center;margin-top:10px' id='lprof_dropdown' class='dropdown'><button class='btn btn-secondary dropdown-toggle' type='button' id='dropdownMenuButton' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>Choose a function to profile!</button>" +
                "<div class='dropdown-menu' aria-labelledby='dropdownMenuButton'>"
    for(fdef in fdefs) {
        lprof_str += "<a class='dropdown-item' href='#' id='" + fdef + "_opt' >" + fdefs[fdef]["name"] + "</a>"
    }
    lprof_str += "</div></div>"

    div.innerHTML += lprof_str
}

function bind_lprof_btns(fdefs) {
    var evt = undefined
    for(fdef in fdefs) {
        var fdef_opt = document.getElementById(fdef + "_opt")
        fdef_opt.addEventListener('click', display_lp_graph.bind(evt, fdefs[fdef]))
    }
}