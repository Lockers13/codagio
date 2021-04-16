const analysis_view_url = "http://localhost:8000/code/analysis/"

fetch(analysis_view_url + soln_id) 
.then(response => response.json())
.then(function (data) {
    console.log(data)
})