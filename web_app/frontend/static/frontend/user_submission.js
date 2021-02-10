
$("#sub_form").submit(function (e) {
    e.preventDefault();
    let post_data = $(this).serialize()
    $.post("http://localhost:8000/submission/", post_data)
        .done(function(data) {
            console.log(data);
        });
});