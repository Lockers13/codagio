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
        let analysis = JSON.parse(resp_data)
        console.log(analysis)
        let scores = analysis["scores"]
        let comp_stats = analysis["comp_stats"][0]
        let fdefs = analysis["fdefs"]
        let comp_str = skel_str = lprof_str = ""
        let result = scores["overall_score"]
        let samp_skels = analysis["samp_skels"]
        // make global collapsible visible
        document.getElementById("accordion").style.visibility = "visible"
        let bd_collapse = document.getElementById("breakdown_collapse")
        let comp_collapse = document.getElementById("comp_collapse")
        let lp_collapse = document.getElementById("lp_collapse")
        let sp_collapse = document.getElementById("sp_collapse")
        let result_p = document.getElementById("result")
        if(result == "100.0%") {
            result_p.style.color = "green"
            result_p.innerHTML = "<br>Congratulations, your code passed all our tests!...<br>Now check out some of your feedback below:"
            write_breakdown(bd_collapse, scores)
            write_comp(comp_collapse, comp_stats, comp_str)
            write_skeleton(sp_collapse, samp_skels, skel_str)
            write_lprof(lp_collapse, fdefs, lprof_str)
            
        }
        else {
            result_p.style.color = "red"
            result_p.innerHTML = "<br>Oops, looks like your code doesn't produce the correct outputs...<br><br>Please Try again! But first, why not check out some feedback below?"
            // do quick marks breakdown and comparison on failure
            write_breakdown(bd_collapse, scores)
            write_comp(comp_collapse, comp_stats, comp_str)
            write_skeleton(sp_collapse, samp_skels, skel_str)
            lp_collapse.innerHTML ="<p>Sorry, you have to pass all tests to qualify for line profiling!<p>"
            }
        })
    .fail(function(resp_data) {console.log(resp_data)})

});

function write_breakdown(collapsible, scores) {
    collapsible.innerHTML = ""
    let breakdown = "<h3 style='text-align:left;'>Quick Results Breakdown</h3>" +
                "<p style='text-align:left;' class='lead'>Let's see where you went right and where you went wrong" + 
                "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" + 
                "<thead><tr><th class='topline scope='col'>Test #</th><th class='topline' scope='col'>Status</th><th class='topline' scope='col'>Input Length</th><th class='topline' scope='col'>Input Type</th></tr></thead><tbody>"
    let count = 1;
    for (test_key in scores) {
        if(test_key == "overall_score")
            continue
        breakdown += "<tr><th scope='row'>" + count++ + "</th>"  +
            "<td>" + scores[test_key]["status"] + "</td>" + 
            "<td>" + scores[test_key]["input_length"] + "</td>" +
            "<td>" + scores[test_key]["input_type"] + "</td></tr>"
    }
    breakdown += "</tbody></table></p>"
    collapsible.innerHTML += breakdown
}

function write_comp(collapsible, comp_stats, comp_str) {
    collapsible.innerHTML = ""
    comp_str += "<h3 style='text-align:left;'>Code Comparison</h3>" +
            "<p style='text-align:left;' class='lead'>Let's see how you match up structurally with the desired solution" + 
            "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" + 
            "<thead><tr><th class='topline' scope='col'>Your Code</th><th class='topline' scope='col'>Our Code</th></tr></thead><tbody>"
    for(let i = 0; i < comp_stats.length; i++) {
        if(comp_stats[i][0].startsWith("skeleton"))
            continue
        comp_str += "<tr><th scope='row'>" + comp_stats[i][0] + "</th>"  +
            "<td>" + comp_stats[i][1] + "</td></tr>"
    }
    comp_str += "</tbody></table></p>"
    collapsible.innerHTML += comp_str
}

function write_skeleton(collapsible, skels, skel_str) {
    collapsible.innerHTML = ""
    skel_str += "<h3 style='text-align:left;'>Our Sample Solution:</h3><hr><br><p style='text-align:left;margin-left:10%'>"
    for(let i = 0; i < skels.length; i++) {
        let skeleton = skels[i]
        for(let j = 0; j < skeleton.length; j++) {
            real_str = skeleton[j].replace(/\s/g, '&nbsp')
            skel_str += "<b><i>" + real_str + "</i></b><br>"
        }
    }
    skel_str += "</p>"
    collapsible.innerHTML += skel_str
}

function write_lprof(collapsible, fdefs, lprof_str) {
    collapsible.innerHTML = ""
    lprof_str += "<h3 style='text-align:left;'>Line Profiling</h3>" +
        "<p style='text-align:left;' class='lead'>Check out the performance of your code in more detail:" + 
        "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" + 
        "<thead><tr><th class='topline' scope='col'>Line #</th><th class='topline' scope='col'># Hits</th><th class='topline' scope='col'>% Time</th><th class='topline' scope='col'>Real Time</th><th class='topline' scope='col'>Contents</th></tr></thead><tbody>"

    for(fdef in fdefs) {
        rt = parseFloat(fdefs[fdef]["cum_time"])
        count = 1
        lprof_dict = fdefs[fdef]["line_profile"]
        for(lprof in lprof_dict) {
            hits = lprof_dict[lprof]["hits"]
            p_time = parseFloat(lprof_dict[lprof]["%time"])
            contents = lprof_dict[lprof]["contents"]
            real_time = Math.round((rt * p_time + Number.EPSILON) * 1000) / 1000
            let bar_colour = p_time < 15? (p_time < 10? "green": "orange"): "red";
            lprof_str += "<tr><th scope='row'>" + count++ + "</th>"  +
            "<td style='height:5px;colour:" + bar_colour + ";'>" + hits + "</td>" + 
            "<td style='height:5px;colour:" + bar_colour + ";'>" + p_time + "</td>" +
            "<td style='height:5px;colour:" + bar_colour + ";'>" + real_time + "</td>" +
            "<td style='height:5px;colour:" + bar_colour + ";'>" + contents + "</td></tr>"
            }
        }
        lprof_str += "</tbody></table></p>"
        collapsible.innerHTML += lprof_str
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
        fontSize: 15, // number | string: set the font size to this many pixels
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