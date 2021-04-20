const delete_base_url = "http://localhost:8000/users/profile/delete/problem/"
const delete_response_url = "http://localhost:8000/users/profile/delete_response/"

var problem_code_div = document.getElementById("problem_code_div")
var problem_description_div = document.getElementById("problem_description_div")

var detailed_stats_div = document.getElementById("detailed_stats_div")

var ctx = document.getElementById('myChart').getContext('2d');
ctx.canvas.width = 700;
ctx.canvas.height = 500;

var container_header = document.getElementById("container_header")

var problem_description = JSON.parse(document.getElementById("problem_description").textContent)
var problem_name = JSON.parse(document.getElementById("problem_name").textContent)
var problem_analysis = JSON.parse(document.getElementById("problem_analysis").textContent)
var problem_code = problem_analysis["code_data"]

var fdefs = problem_analysis["fdefs"]

var detailed_stats_str = ""

detailed_stats_str += "<p>Total computation time: " + problem_analysis["udef_func_time_tot"] + "s</p>"
detailed_stats_str += "<p>By function: " + "<ul>"

for (fdef in fdefs) {
    detailed_stats_str += "<li>" + fdefs[fdef]["name"] + " => " + fdefs[fdef]["cum_time"] + "s</li>"
}
detailed_stats_str += "</ul></p>"

detailed_stats_div.innerHTML = detailed_stats_str

problem_code_div.innerHTML = get_json_text(problem_code, code = true)
problem_description_div.innerHTML = get_json_text(problem_description.split('\n'))


container_header.innerHTML = problem_name + "<br><br>"

display_scatterplot()

var delete_button = document.getElementById("delete_button")
delete_button.addEventListener('click', function (e) {
    e.preventDefault()
    document.getElementById("confirm_delete").onclick = handle_decision
    return
})

function handle_decision(e) {
    var target_id = e.target.id
    if (target_id == "confirm") {
        var delete_response = document.getElementById("delete_response")
        $.ajax({
            url: delete_base_url + prob_id,
            method: "DELETE",
            headers: { 'X-CSRFToken': csrf_token },
        }).done(function (response) {
            window.location.href = delete_response_url
        }).fail(function (error) {
            delete_response.innerHTML = "<p style='color:red'>Uh oh, there was an error deleting your solution!</p>"
        });
    }
    else
        return
}

function get_json_text(json_arr, code = false) {
    var text_to_write = ""
    for (let i = 0; i < json_arr.length; i++) {
        if (code)
            text_to_write += "<span><i>" + json_arr[i].replace(/\s/g, '&nbsp') + "</i></span><br>"
        else
            text_to_write += "<span>" + json_arr[i].replace(/\s/g, '&nbsp') + "</span><br>"
    }
    return text_to_write
}

function display_scatterplot() {
    // document.getElementById("graph_heading").innerHTML = "<p style='margin:50px 0px 0px 0px;text-align:center'>Time spent in function => " + fdef["cum_time"] + " seconds</p>"
    try {
        window.chart.destroy();
    }
    catch (err) {
        ;
    }

    var labels = []
    var dataset = [
        {
            label: "%",
            data: [{ x: 1, y: 3 }, { x: 2, y: 8 }, { x: 3, y: 9 }],
            backgroundColor: "white"
        },
    ];

    var options = {
        maintainAspectRatio: false,
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
                stacked: true,
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '#',
                },
                ticks: {

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