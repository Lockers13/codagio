const editor = init_editor()
const func_line_offset = 3
const code_analysis_url = "http://localhost:8000/api/code/analysis/"

const ERROR_CODES = {
    10: "Uh-oh...Looks like your code threw a run-time error!",
    11: "Uh-oh...Looks like there's a syntax error in your code!",
    12: "Sorry, your code violates one of the problem constraints!",
    13: "Sorry, it seems like there's something wrong with our server...check back later!",
    14: "Uh-oh...Your code timed out, please try again!",
    15: "Sorry, there was a problem with your submission, please make sure everything is in order, and try again!"
}

let error_paragraph = document.getElementById("error_message")
let loader = document.getElementById('loader');
let submitbtn = document.getElementById('sub_btn');
let desc = document.getElementById('description');
let result_section = document.getElementById('result');
let overall = document.getElementById('overall_score');
let back = document.getElementById('go_back');
let collapse_section = document.getElementById('collapse_section');

var ctx = document.getElementById('myChart').getContext('2d');
ctx.canvas.width = 700;
ctx.canvas.height = 500;

submitbtn.addEventListener('click', function () {
    submitbtn.style.visibility = 'hidden';
    desc.style.display = 'none';
    loader.style.display = 'block';
});

back.addEventListener('click', reset);

function toggleContent(content) {
    if (content.style.maxHeight) {
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + 'px';
    }
  }

function collapseAllOpenContent() {
    const colls = document.getElementsByClassName('collapsible');
    for (const coll of colls) {
      if (coll.classList.contains('active')) {
        coll.classList.remove('active');
        toggleContent(coll.nextElementSibling);
      }
    }
  }

function reset() {
    submitbtn.style.visibility = 'visible';
    desc.style.display = 'block';
    back.style.display = 'none';
    overall.style.display = 'none';
    collapse_section.style.display = 'none';
    collapseAllOpenContent()
    error_paragraph.innerHTML = ""
}

//Form submission logic
$("#sub_form").submit(function (e) {
    e.preventDefault();
    let sub_text = editor.getValue();
    let submission_length = sub_text.split(/\r\n|\r|\n/).length
    if(submission_length > 1500) {
        error_paragraph.innerHTML = "Sorry, your submission must be less than 1500 lines!"
        loader.style.display = 'none';
        back.style.display = 'block';
        result_section.style.display = 'block';
        return
    }
    let solution_text_box = document.getElementById("solution_text")
    solution_text_box.value = sub_text

    $.ajax({
        url: code_analysis_url,
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
        .done(function (resp_data) {
            let analysis = JSON.parse(resp_data)
            console.log(analysis)
            try {
                var graph_heading = document.getElementById("graph_heading")
                if(graph_heading != null)
                    graph_heading.innerHTML = ""
            }
            catch(err) {
                ;
            }
            //Get results
            let scores = analysis["scores"]
            let fdefs = analysis["fdefs"]
            let skel_str = lprof_str = overview_str = ""
            let result = Math.round(parseFloat(scores["overall_score"].split("%")[0]) * 100) / 100
            let samp_skels = analysis["samp_skels"]
            //Get sections
            let overview_section = document.getElementById("overview_stats")
            let pseudo_section = document.getElementById('pseudocode');
            let profiling_section = document.getElementById('line_profiling');

            loader.style.display = 'none';
            back.style.display = 'block';
            overall.style.display = 'block';
            overall.innerHTML = '<h1>Total Score: ' + result + '</h1>';
            collapse_section.style.display = 'block';

            if (result >= parseFloat(analysis["pass_threshold"])) {
                overall.style.color = "#06D6A0"
                overall.innerHTML = "<h3>You Scored: " + result + "%</h3>"
                overall.innerHTML += "<br>Congratulations, your code passed the threshold score..!<br>Now check out some of your feedback below:"
                write_skeleton(pseudo_section, samp_skels, skel_str)
                write_overview_stats(overview_section, analysis, overview_str, abs_success=true)
                bind_detail_links(scores)
                write_lprof(profiling_section, fdefs, lprof_str)
                bind_lprof_btns(fdefs)   
            }
            else {
                overall.style.color = "orange"
                overall.innerHTML = "<h3>You Scored: " + result + "%</h3>"
                overall.innerHTML += "<br>Oops, looks like your code doesn't pass our threshold of excellence...<br><br>Please try again! But first, why not check out some feedback below?"
                if(window.chart != undefined)
                    window.chart.destroy()
                profiling_section.innerHTML = "<br>Sorry, you must pass the predetermined threshold of " + parseFloat(analysis["pass_threshold"]) + "% to qualify for line profiling!"
                write_overview_stats(overview_section, analysis, overview_str)
                bind_detail_links(scores)
                write_skeleton(pseudo_section, samp_skels, skel_str)
            }
        })
        .fail(function (resp_data) {
            if(resp_data["status"] == 400) {
                loader.style.display = 'none';
                back.style.display = 'block';
                var error_code = parseInt(resp_data["responseJSON"])
                var message = ERROR_CODES[error_code]

                loader.style.display = 'none';
                back.style.display = 'block';
                result_section.style.display = 'block';
                error_paragraph.innerHTML = message
            }
            else if(resp_data["status"] == 500) {
                loader.style.display = 'none';
                back.style.display = 'block';
                result_section.style.display = 'block';
                error_paragraph.innerHTML = ERROR_CODES[13]
            }

        })
});

function display_lp_graph(fdef) {
    document.getElementById("graph_heading").innerHTML = "<p style='margin:50px 0px 0px 0px;text-align:center'>Time spent in function => " + fdef["cum_time"] + " seconds</p>"
    try {
        window.chart.destroy();
    }
    catch(err) {
        ;
    }
    var lprof_dict = fdef["line_profile"]
    var percentage_times = []
    var line_nos = []

    for(line in lprof_dict) {
        try{
            var p_time = parseFloat(lprof_dict[line]["%time"])
            percentage_times.push(p_time)
        }
        catch(err) {
            percentage_times.push(0.0)
        }
        var line_num = parseInt(line.split("_")[1])
        line_nos.push(line_num - func_line_offset)
    }

    var labels = line_nos
    var dataset = [
        {   
            label: "% of function time spent executing line",
            data: percentage_times,
            backgroundColor: "purple"
        },
    ];

    var options = {
        // onClick: function (e) {
        //     try {
        //         var activePointLabel = this.getElementsAtEvent(e)[0]._model.label;
        //         alert(activePointLabel);
        //     }
        //     catch(err) {
        //         ;
        //     }
        // },
        maintainAspectRatio : false,
        responsive: false,
        scales: {
            xAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '% Time'
                },
                stacked: true,
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: 'Line No.',
                },
                ticks: {
                    max : line_nos[line_nos.length - 1],
                    min : line_nos[0],
                },
                stacked: true,
                barPercentage: 0.4,
            }]
        }
    };

    var content = {
        type: 'horizontalBar',
        data: {
            labels: labels,
            datasets: dataset
        },
        options
    };

    window.chart = new Chart(ctx, content);
}

function write_overview_stats(section, analysis, content_str, abs_success=false) {
    section.innerHTML = ""
    var ufunc_tot = Math.round(parseFloat(analysis["udef_func_time_tot"]) * 10000) / 10000
    var ref_func_tot = Math.round(parseFloat(analysis["ref_time"]) * 10000) / 10000
    if(abs_success) {
        content_str += "<br><p>Total Time spent executing your functions: " + ufunc_tot + "</p>"
        content_str += "<p>Total Time spent executing functions of reference program: " + ref_func_tot + "</p><br>"
        content_str += "<ul>"
        var fdefs = analysis["fdefs"]
        for(fdef in fdefs) {
            content_str += "<li>Function Name: " + fdefs[fdef]["name"] + "<br>" +
                            "Cumulative Time spent in function: " + fdefs[fdef]["cum_time"] + "</li><br>"
        }
        content_str += "</ul><br>"
    }
    content_str += "<p style='text-align:left;margin:20px 0px 20px 0px;' class='lead'>Let's see how you fared in more detail...</p>" +
    "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table'>" +
    "<thead><tr><th style='color:white' class='topline scope='col'>Test #</th><th style='color:white' class='topline' scope='col'>Status</th><th style='color:white' class='topline' scope='col'>Input Length</th><th style='color:white' class='topline' scope='col'>Input Type</th><th style='color:white' class='topline' scope='col'>Detailed Stats</th></tr></thead><tbody>"
    let count = 1
    let scores = analysis["scores"]
    for (test_key in scores) {
        if (test_key == "overall_score")
            continue
        content_str += "<tr><th scope='row' style='color:white'>" + count++ + "</th>" +
            "<td style='color:white'>" + scores[test_key]["status"] + "</td>" +
            "<td style='color:white'>" + scores[test_key]["input_length"] + "</td>" +
            "<td style='color:white'>" + scores[test_key]["input_type"] + "</td>"
        if (parseFloat(scores[test_key]["detailed_stats"]["success_rate"]) != 100.0) {
            content_str += "<td style='color:red'><a class='link-danger' style='color:red;cursor:pointer;' name='detail_link' id='" + test_key + "' data-toggle='modal' data-target='#exampleModalCenter'>Failed - <br>(See More)</a></td>"
        }
        else {
            content_str += "<td style='color:green;'>Passed - <br>(100%)</td>"
        }
        content_str += "</tr>"
    }
    content_str += "</tbody></table></p>"
    section.innerHTML += content_str
}

function bind_lprof_btns(fdefs) {
    var evt = undefined
    for(fdef in fdefs) {
        var fdef_opt = document.getElementById(fdef + "_opt")
        fdef_opt.addEventListener('click', display_lp_graph.bind(evt, fdefs[fdef]))
    }
}

function bind_detail_links(scores) {
    var detail_links = document.getElementsByName("detail_link")
    for(var i = 0; i < detail_links.length; i++) {
        var test_key = detail_links[i].id
        var evt = undefined
        detail_links[i].addEventListener('click', write_detailed_stats.bind(evt, scores, test_key))
    }
}

function write_detailed_stats(scores, test_key) {
    var modal_body = document.getElementById("modal_body")
    modal_body.innerHTML = "<ul>"
    var detailed_stats = scores[test_key]["detailed_stats"]
    modal_body.innerHTML += "<li>Number of Tests: " + detailed_stats["num_tests"] + "</li><br>" +
                        "<li>Number of Correct Outputs: " + detailed_stats["num_correct"] + "</li>" + 
                        "<li>Success Rate: " + detailed_stats["success_rate"] + "</li><br>" + 
                        "<li>Number of Incorrect Outputs: " + detailed_stats["num_failures"] + "</li>" + 
                        "<li>Failure Rate: " + detailed_stats["failure_rate"] + "</li></ul>" + 
                        "<br><u>A sample of your correct outputs:<u><ul>"

    for(var m_index = 0; m_index < detailed_stats["matches"].length; m_index++) {
        modal_body.innerHTML += "<li  style='color:green;padding-left:3em'>Your Output: " + detailed_stats["matches"][m_index] + "</li>"
    }
    modal_body.innerHTML += "</ul><br><u>A sample of your incorrect outputs:<u><ul>"
    for(var mm_index = 0; mm_index < detailed_stats["mismatches"].length; mm_index++) {
        modal_body.innerHTML += "<li  style='color:red;padding-left:3em'>Your Output: " + detailed_stats["mismatches"][mm_index][0] + " - VS - Expected Output: " + detailed_stats["mismatches"][mm_index][1] + "</li>"
    }
    modal_body.innerHTML += "</ul"
}

function write_skeleton(collapsible, skels, skel_str) {
    collapsible.innerHTML = ""
    skel_str += "<p style='color:white;font-style:italic;margin:20px 0px; padding: 10px 10px;' class='table'>"
    for (let i = 0; i < skels.length; i++) {
        let skeleton = skels[i]
        for (let j = 0; j < skeleton.length; j++) {
            real_str = skeleton[j].replace(/\s/g, '&nbsp')
            skel_str += "" + real_str + "<br>"
        }
        skel_str += "<br>"
    }
    skel_str += "</p>"
    collapsible.innerHTML += skel_str
}

function write_lprof(collapsible, fdefs, lprof_str) {
    collapsible.innerHTML = ""
    lprof_str += "<div style='text-align:center;margin-top:10px' id='lprof_dropdown' class='dropdown'><button class='btn btn-secondary dropdown-toggle' type='button' id='dropdownMenuButton' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>Choose a function to profile!</button>" +
                "<div class='dropdown-menu' aria-labelledby='dropdownMenuButton'>"
    for(fdef in fdefs) {
        lprof_str += "<a class='dropdown-item' href='#' id='" + fdef + "_opt' >" + fdefs[fdef]["name"] + "</a>"
    }
    lprof_str += "</div></div>"

    collapsible.innerHTML += lprof_str
}

// Main editor initialization function
function init_editor() {
    let editor = ace.edit("editor");
    var main_signature = document.getElementById("main_signature").innerHTML

    editor.setValue(main_signature + "\n    ### write your code here...");           

    editor.setOptions({
        // editor options
        selectionStyle: 'text',// "line"|"text"
        highlightActiveLine: true, // boolean
        highlightSelectedWord: true, // boolean
        readOnly: false, // boolean: true if read only
        cursorStyle: 'smooth', // "ace"|"slim"|"smooth"|"wide"
        mergeUndoDeltas: true, // false|true|"always"
        behavioursEnabled: true, // boolean: true if enable custom behaviours
        wrapBehavioursEnabled: true, // boolean
        autoScrollEditorIntoView: true, // boolean: this is needed if editor is inside scrollable page
        keyboardHandler: null, // function: handle custom keyboard events

        // renderer options
        animatedScroll: true, // boolean: true if scroll should be animated
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
        vScrollBarAlwaysVisible: false, // boolean: true if the vertical scroll bar should be shown regardless
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