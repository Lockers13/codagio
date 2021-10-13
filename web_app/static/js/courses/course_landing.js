let delete_base_url = "http://localhost:8000/api/courses/delete/problem/"
let delete_response_url = "http://localhost:8000/courses/delete_response/problem/"

var delete_buttons = document.getElementsByName("del_btn")
for(let i = 0; i < delete_buttons.length; i++) {
    let delete_button = delete_buttons[i]
    let del_btn_id = delete_button.id.split("_")[1]
    var conf_btn = document.getElementById("confirm_delete_" + del_btn_id)
    console.log(conf_btn)
    conf_btn.addEventListener('click', function(e) {
        console.log(delete_base_url + del_btn_id)
    })

}



// function handle_decision(e) {
//     var target_id = e.target.id
//     if (target_id == "confirm") {
//         var delete_response = document.getElementById("delete_response")
//         $.ajax({
//             url: delete_base_url + prob_id,
//             method: "DELETE",
//             headers: { 'X-CSRFToken': csrf_token },
//         }).done(function (response) {
//             window.location.href = delete_response_url
//         }).fail(function (error) {
//             delete_response.innerHTML = "<p style='color:red'>Uh oh, there was an error deleting your solution!</p>"
//         });
//     }
// }
