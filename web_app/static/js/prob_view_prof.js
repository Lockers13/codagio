var problem_code_div = document.getElementById("problem_code_div")
var problem_description_div = document.getElementById("problem_description_div")

var container_header =  document.getElementById("container_header")

var problem_description = JSON.parse(document.getElementById("problem_description").textContent)
var problem_code = JSON.parse(document.getElementById("problem_code").textContent)
var problem_name = JSON.parse(document.getElementById("problem_name").textContent)

problem_description_div.innerHTML = get_json_text(problem_description.split('\n'))
problem_code_div.innerHTML = get_json_text(problem_code, code=true)

container_header.innerHTML = problem_name +"<br><br>"

function get_json_text(json_arr, code=false) {
    var text_to_write = ""
    console.log(json_arr)
    for(let i = 0; i < json_arr.length; i++) {
        if(code)
            text_to_write += "<span><i>" + json_arr[i].replace(/\s/g, '&nbsp') + "</i></span><br>"
        else
            text_to_write += "<span>" + json_arr[i].replace(/\s/g, '&nbsp') + "</span><br>"
    }
    return text_to_write
}