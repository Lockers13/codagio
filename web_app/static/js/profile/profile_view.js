const profstats_url = "http://localhost:8000/api/profile/stats/"
const retry_url = "http://localhost:8000/code/solution/"

fetch(profstats_url) 
.then(response => response.json())
.then(function (data) {
    const soln_base_url = 'http://localhost:8000/users/profile/solution/'
    const prob_base_url = 'http://localhost:8000/users/profile/problem/'

    var toggle = document.getElementById("toggle")

    toggle.addEventListener('click', function() {
        var stats_view = document.getElementById("stats_view")
        stats_view.innerHTML = ""
        var build_string = ""
        if(toggle.value == 0) {
            stats_list = data[0]
            console.log(stats_list)
            build_string += "<h1 id='stats_header'><u>Your Saved Solutions</u></h1><br>"
            if(stats_list.length == 0) {
                build_string += "<p>Sorry, you have no saved solutions to show!</p>"
            }
            else {
                for(let i = 0; i < stats_list.length; i++) {
                    build_string += "<div id='accordion'>"
                    build_string += "<div class='card' style='width:80%;margin: 0 auto;background-color:#101010;'>"
                    build_string += "<div class='card-header' id='heading" + i +"'>"
                    build_string += "<h5 class='mb-0'>"
                    build_string += "<button style='color:#06D6A0;' class='btn btn-link' data-toggle='collapse' data-target='#collapse" + i + "' aria-expanded='true' aria-controls='collapse" + i +"'>" + stats_list[i]["problem__name"] + "</button></h5></div>"
                    build_string += "<div id='collapse" + i +"' class='collapse' aria-labelledby='heading" + i + "' data-parent='#accordion'>"
                    build_string += "<div class='card-body'>"
                    build_string += "<p>Your Score: " + stats_list[i]["analysis__scores__overall_score"] + "</p>" 
                    build_string += "<div class='text-center'>"
                    build_string += "<a href='" + soln_base_url + "view/?soln_id=" +  stats_list[i]["id"] + "&prob_id=" + stats_list[i]["problem__id"] + "'><button type='button' class='text-center go_btn'>View More</button></a></div>"
                    build_string += "<div class='text-center' style='margin-top:10px;'>"
                    build_string += "<a href='" + retry_url + stats_list[i]["problem__id"] + "'><button type='button' class='text-center go_btn' style='background-color:#1d2b5b'>Try Again</button></a>"
                    build_string += "</div><p class='problem_author'>Problem Created by " + stats_list[i]["problem__author__user__username"]
                    build_string +=  " on " + stats_list[i]["problem__date_submitted"] + "</p></div>"
                    build_string += "</div></div></div></div>"
                }
                build_string += "</div>"
            }
            stats_view.innerHTML += build_string
            toggle.innerHTML = "View Your Uploaded Problems"
            toggle.value = 1
          
        }
        else if(toggle.value == 1) {
            stats_list = data[1]
            console.log(stats_list)
            build_string += "<h1 id='stats_header'><u>Your Uploaded Problems</u></h1><br>"
            if(stats_list.length == 0) {
                build_string += "<p>Sorry, you have no uploaded problems to show!</p>"
            }
            else {
                for(let i = 0; i < stats_list.length; i++) {
                    build_string += "<div id='accordion'>"
                    build_string += "<div class='card' style='width:80%;margin: 0 auto;background-color:#101010;'>"
                    build_string += "<div class='card-header' id='heading" + i +"'>"
                    build_string += "<h5 class='mb-0'>"
                    build_string += "<button style='color:#06D6A0;' class='btn btn-link' data-toggle='collapse' data-target='#collapse" + i + "' aria-expanded='true' aria-controls='collapse" + i +"'>" + stats_list[i]["name"] + "</button></h5></div>"
                    build_string += "<div id='collapse" + i +"' class='collapse' aria-labelledby='heading" + i + "' data-parent='#accordion'>"
                    build_string += "<div class='card-body'>"
                    build_string += "<p>Difficulty: " + stats_list[i]["metadata__difficulty"] + "</p>" 
                    build_string += "<p>Category: " + stats_list[i]["metadata__category"] + "</p>" 
                    build_string += "<p>Pass Threshold: " + stats_list[i]["metadata__pass_threshold"] + "</p>" 
                    // build_string += "<p>Description: " + stats_list[i]["metadata__description"] + "</p>" 
                    build_string += "<a href='" + prob_base_url + "view/?prob_id=" + stats_list[i]["id"] + "'>"
                    build_string += "<div class='text-center'>"
                    build_string += "<button type='button' class='text-center go_btn'>View More</button>"
                    build_string += "</div></a><p class='problem_author'>Problem Created on " + stats_list[i]["date_submitted"] + "</p></div>"
                    build_string += "</div></div></div></div>"
                }
                build_string.innerHTML += "</div>"
            }
            stats_view.innerHTML += build_string
            toggle.innerHTML = "View Your Saved Solutions"
            toggle.value = 0
        }
    })
})
.then(function() {
    toggle.click()
})
