$("#sub_form").submit(function (e) {
    e.preventDefault();
    console.log(editor.getValue())
    return
    $.ajax( {
        url: 'http://localhost:8000/code/analysis/',
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    .done(function(resp_data) {console.log(resp_data)})
    .fail(function(resp_data) {console.log(resp_data)})
});

