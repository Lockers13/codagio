const editor = init_editor()

$("#sub_form").submit(function(e) {
    e.preventDefault();
    let sub_text = editor.getValue();
    let solution_text_box = document.getElementById("solution_text")

    solution_text_box.value = sub_text

    $.ajax( {
        url: 'http://localhost:8000/code/analysis/',
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
    .done(function(resp_data) {
        console.log(resp_data)
        let analysis = JSON.parse(resp_data)
        let scores = analysis["scores"]
        let result = scores["overall_score"]
        let analysis_div = document.getElementById("analysis")
        let result_p = document.getElementById("result")
        if(result == "100.0") {
            result_p.style.color = "green"
            result_p.innerHTML = "Congratulations, you passed all our tests!"
        }
        else {
            result_p.style.color = "red"
            result_p.innerHTML = "<br>Oops, looks like your code doesn't produce the correct outputs...please try again!"
            // do quick marks breakdown on failure
            write_breakdown(analysis_div, scores)
            
            }
        })
    .fail(function(resp_data) {console.log(resp_data)})

});

function write_breakdown(analysis_div, scores) {
    let breakdown = "<h1>Quick Results Breakdown</h1>" +
                "<p class='lead'>Let's see where you went right and where you went wrong" + 
                "<table style='max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" + 
                "<thead><tr><th scope='col'>Test #</th><th scope='col'>Status</th><th scope='col'>Input Length</th><th scope='col'>Input Type</th></tr></thead><tbody>"
    let count = 1;
    for (test_key in scores) {
        if(test_key == "overall_score")
            continue
        breakdown += "<tr><th scope='row'>" + count++ + "</th>"  +
            "<td>" + scores[test_key]["status"] + "</td>" + 
            "<td>" + scores[test_key]["input_length"] + "</td>" +
            "<td>" + scores[test_key]["input_type"] + "</td>"
    }
    breakdown += "</tbody></table></p>"
    analysis_div.innerHTML += breakdown
}

function init_editor() {
    let editor = ace.edit("editor");
        editor.setValue("Write your code here...");

        editor.setOptions({
        // editor options
        selectionStyle: 'text',// "line"|"text"
        highlightActiveLine: false, // boolean
        highlightSelectedWord: true, // boolean
        readOnly: false, // boolean: true if read only
        cursorStyle: 'ace', // "ace"|"slim"|"smooth"|"wide"
        mergeUndoDeltas: true, // false|true|"always"
        behavioursEnabled: true, // boolean: true if enable custom behaviours
        wrapBehavioursEnabled: true, // boolean
        autoScrollEditorIntoView: undefined, // boolean: this is needed if editor is inside scrollable page
        keyboardHandler: null, // function: handle custom keyboard events

        // renderer options
        animatedScroll: false, // boolean: true if scroll should be animated
        displayIndentGuides: false, // boolean: true if the indent should be shown. See 'showInvisibles'
        showInvisibles: false, // boolean -> displayIndentGuides: true if show the invisible tabs/spaces in indents
        showPrintMargin: true, // boolean: true if show the vertical print margin
        printMarginColumn: true, // number: number of columns for vertical print margin
        printMargin: undefined, // boolean | number: showPrintMargin | printMarginColumn
        showGutter: true, // boolean: true if show line gutter
        fadeFoldWidgets: false, // boolean: true if the fold lines should be faded
        showFoldWidgets: true, // boolean: true if the fold lines should be shown ?
        showLineNumbers: true,
        highlightGutterLine: false, // boolean: true if the gutter line should be highlighted
        hScrollBarAlwaysVisible: false, // boolean: true if the horizontal scroll bar should be shown regardless
        vScrollBarAlwaysVisible: true, // boolean: true if the vertical scroll bar should be shown regardless
        fontSize: 14, // number | string: set the font size to this many pixels
        fontFamily: undefined, // string: set the font-family css value
        maxLines: undefined, // number: set the maximum lines possible. This will make the editor height changes
        minLines: undefined, // number: set the minimum lines possible. This will make the editor height changes
        maxPixelHeight: 0, // number -> maxLines: set the maximum height in pixel, when 'maxLines' is defined. 
        scrollPastEnd: 0, // number -> !maxLines: if positive, user can scroll pass the last line and go n * editorHeight more distance 
        fixedWidthGutter: false, // boolean: true if the gutter should be fixed width
        theme: 'ace/theme/idle_fingers', // theme string from ace/theme or custom?

        // mouseHandler options
        scrollSpeed: 2, // number: the scroll speed index
        dragDelay: 0, // number: the drag delay before drag starts. it's 150ms for mac by default 
        dragEnabled: true, // boolean: enable dragging
        focusTimeout: 0, // number: the focus delay before focus starts.
        tooltipFollowsMouse: true, // boolean: true if the gutter tooltip should follow mouse

        // session options
        firstLineNumber: 1, // number: the line number in first line
        overwrite: false, // boolean
        newLineMode: 'auto', // "auto" | "unix" | "windows"
        useWorker: true, // boolean: true if use web worker for loading scripts
        useSoftTabs: true, // boolean: true if we want to use spaces than tabs
        tabSize: 4, // number
        wrap: false, // boolean | string | number: true/'free' means wrap instead of horizontal scroll, false/'off' means horizontal scroll instead of wrap, and number means number of column before wrap. -1 means wrap at print margin
        indentedSoftWrap: true, // boolean
        foldStyle: 'markbegin', // enum: 'manual'/'markbegin'/'markbeginend'.
        mode: 'ace/mode/python' // string: path to language mode 
        })

    return editor;
}

