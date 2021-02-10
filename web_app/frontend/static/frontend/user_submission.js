
$("#sub_form").submit(function (e) {
    e.preventDefault();
    let post_data = $(this).serializeArray()
    console.log(post_data)
    $.ajax( {
        url: 'http://localhost:8000/submission/',
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    return
    $.post("http://localhost:8000/submission/", post_data)
        .done(function(data) {
           // console.log(data);
        });
});