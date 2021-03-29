const editor = init_editor()
const func_line_offset = 3

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
}

//Form submission logic
$("#sub_form").submit(function (e) {
    e.preventDefault();
    let sub_text = editor.getValue();
    let solution_text_box = document.getElementById("solution_text")


    solution_text_box.value = sub_text

    $.ajax({
        url: 'http://localhost:8000/code/analysis/',
        type: 'POST',
        data: new FormData(this),
        processData: false,
        contentType: false,
    })
        .done(function (resp_data) {
            let analysis = JSON.parse(resp_data)
            console.log(analysis)
            //Get results
            let scores = analysis["scores"]
            let comp_stats = analysis["comp_stats"][0]
            let fdefs = analysis["fdefs"]
            let comp_str = skel_str = lprof_str = overview_str = ""
            let result = scores["overall_score"]
            let samp_skels = analysis["samp_skels"]
            //Get sections
            let overview_section = document.getElementById("overview_stats")
            // let breakdown_section = document.getElementById('breakdown');
            // let comparison_section = document.getElementById('comparison');
            let pseudo_section = document.getElementById('pseudocode');
            let profiling_section = document.getElementById('line_profiling');
            // let failure_section = document.getElementById('fail_stats');
            // let fail_btn = document.getElementById('fail_btn');
            // let lp_btn = document.getElementById('lp_btn');
            // make global collapsible visible
            loader.style.display = 'none';
            back.style.display = 'block';
            overall.style.display = 'block';
            overall.innerHTML = '<h1>Total Score: ' + result + '</h1>';
            collapse_section.style.display = 'block';

            var lp_btn = document.getElementById("lp_btn")

            if (result == "100.0%") {
                overall.style.color = "#06D6A0"
                overall.innerHTML = "<br>Congratulations, your code passed all our tests!...<br>Now check out some of your feedback below:"

                //lp_btn.addEventListener('click', display_lp_graph.bind(e, fdefs["fdef_1"]))
                // write_breakdown(breakdown_section, scores)
                // write_comp(comparison_section, comp_stats, comp_str)
                write_skeleton(pseudo_section, samp_skels, skel_str)
                write_overview_stats(overview_section, analysis, overview_str, success=true)
                write_lprof(profiling_section, fdefs, lprof_str)
                bind_lprof_btns(fdefs)   
            }
            else {
                overall.style.color = "#FF3E6C"
                overall.innerHTML = "<br>Oops, looks like your code doesn't produce the correct outputs...<br><br>Please Try again! But first, why not check out some feedback below?"
                if(window.chart != undefined)
                    window.chart.destroy()
                profiling_section.innerHTML = "<br>Sorry, you must pass all tests to qualify for line profiling!"
                write_overview_stats(overview_section, analysis, overview_str, success=false)
                bind_fail_btns(scores)
                // do quick marks breakdown and comparison on failure
                // write_breakdown(breakdown_section, scores)
                // write_comp(comparison_section, comp_stats, comp_str)
                write_skeleton(pseudo_section, samp_skels, skel_str)
                // profiling_section.innerHTML ="<p class='text-center' style='margin:20px 0px;'>Sorry, you have to pass all tests to qualify for line profiling!<p>"
                // write_failure(failure_section, scores)
            }
        })
        .fail(function (resp_data) {
            loader.style.display = 'none';
            back.style.display = 'block';
            console.log("Broken code", resp_data)
            if (resp_data["responseJSON"] == "POST NOT OK: potentially unsafe code!")
                loader.style.display = 'none';
            back.style.display = 'block';
            result_section.style.display = 'block';
            result_section.innerHTML = "<br><b><i>Sorry, we cannot trust the submitted code as it does not abide by our rules. Please try again!</i></b>"
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
    console.log(lprof_dict)
    var percentage_times = []
    var line_nos = []
    var bar_colors = []
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
    var max_pc = Math.max.apply(null, percentage_times)

    var labels = line_nos
    var dataset = [
        {   
            label: "% of function time spent executing line",
            data: percentage_times,
            backgroundColor: "green"
        },
    ];

    var options = {
        onClick: function (e) {
            try {
                var activePointLabel = this.getElementsAtEvent(e)[0]._model.label;
                alert(activePointLabel);
            }
            catch(err) {
                ;
            }

        },
        maintainAspectRatio : false,
        responsive: false,
        scales: {
            xAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: '% Time'
                },
                stacked: true
            }],
            yAxes: [{
                scaleLabel: {
                    display: true,
                    labelString: 'Line No.'
                },
                ticks: {
                    max : line_nos[line_nos.length - 1],
                    min : line_nos[0],
                    fixedStepSize: 0.1
                },
                stacked: true
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

function write_overview_stats(section, analysis, content_str, success=false) {
    section.innerHTML = ""
    if(success) {
        
        content_str += "<br><p>Total Time spent executing your functions: " + analysis["udef_func_time_tot"] + "</p>"
        content_str += "<p>Total Time spent executing functions of reference program: " + analysis["ref_time"] + "</p><br>"
        content_str += "<ul>"
        var fdefs = analysis["fdefs"]
        for(fdef in fdefs) {
            content_str += "<li>Function Name: " + fdefs[fdef]["name"] + "<br>" +
                            "Cumulative Time spent in function: " + fdefs[fdef]["cum_time"] + "</li><br>"
        }
        content_str += "</ul>"
        section.innerHTML += content_str
    }
    else {
        content_str += "<p style='text-align:left;margin:20px 0px 20px 0px;' class='lead'>Let's see where you went right and where you went wrong </p>" +
        "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table'>" +
        "<thead><tr><th style='color:white' class='topline scope='col'>Test #</th><th style='color:white' class='topline' scope='col'>Status</th><th style='color:white' class='topline' scope='col'>Input Length</th><th style='color:white' class='topline' scope='col'>Input Type</th><th style='color:white' class='topline' scope='col'>Failure Stats</th></tr></thead><tbody>"
        let count = 1
        let scores = analysis["scores"]
        for (test_key in scores) {
            if (test_key == "overall_score")
                continue
            content_str += "<tr><th scope='row' style='color:white'>" + count++ + "</th>" +
                "<td style='color:white'>" + scores[test_key]["status"] + "</td>" +
                "<td style='color:white'>" + scores[test_key]["input_length"] + "</td>" +
                "<td style='color:white'>" + scores[test_key]["input_type"] + "</td>"
            if (scores[test_key]["failure_stats"] != undefined) {
                content_str += "<td style='color:red'><a class='link-danger' style='color:red;cursor:pointer;' name='fail_link' id='" + test_key + "' data-toggle='modal' data-target='#exampleModalCenter'>See More</a></td>"
                // for (fail_key in scores[test_key]["failure_stats"]) {
                //     content_str += "<td>" + scores[test_key]["failure_stats"][fail_key] + "</td>"
                // }
            }
            else {
                content_str += "<td style='color:white'> None </td>"
            }
            content_str += "</tr>"
        }
        content_str += "</tbody></table></p>"
        section.innerHTML += content_str
    }
}

function bind_lprof_btns(fdefs) {
    var evt = undefined
    for(fdef in fdefs) {
        var fdef_opt = document.getElementById(fdef + "_opt")
        fdef_opt.addEventListener('click', display_lp_graph.bind(evt, fdefs[fdef]))
    }
}

function bind_fail_btns(scores) {
    var fail_links = document.getElementsByName("fail_link")
    for(var i = 0; i < fail_links.length; i++) {
        var test_key = fail_links[i].id
        var evt = undefined
        //write_fail_stats(scores, test_key)
        fail_links[i].addEventListener('click', write_fail_stats.bind(evt, scores, test_key))
    }
}

function write_fail_stats(scores, test_key) {
    var modal_body = document.getElementById("modal_body")
    modal_body.innerHTML = "<ul>"
    for(fail_stat in scores[test_key]["failure_stats"]) {
        if(fail_stat == "mismatches") {
            modal_body.innerHTML += "<br><u>Some Sample Outputs:<u><ul>"
            for(var mm_index = 0; mm_index < scores[test_key]["failure_stats"][fail_stat].length; mm_index++) {
                modal_body.innerHTML += "<li  style='padding-left:3em'>Your Output: " + scores[test_key]["failure_stats"][fail_stat][mm_index][0] + " - VS - Expected: " + scores[test_key]["failure_stats"][fail_stat][mm_index][1] + "</li>"
            }
            modal_body.innerHTML += "</ul>"
        }
        else {
            modal_body.innerHTML += "<li>" + fail_stat.charAt(0).toUpperCase() + fail_stat.slice(1) + ": " +  scores[test_key]["failure_stats"][fail_stat] + "</li>"
        }
    }
    modal_body.innerHTML += "</ul>"
}

function write_failure(collapsible, scores) {
    collapsible.innerHTML = ""
    let breakdown = "<p style='text-align:left;margin:20px 0px 20px 0px;' class='lead'>Let's take a closer look at where you went wrong</p>" +
        "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" +
        "<thead><tr><th class='topline scope='col'>Test #</th><th class='topline' scope='col'># Inputs</th><th class='topline' scope='col'># Failures</th><th class='topline' scope='col'>Failure Rate</th><th class='topline' scope='col'>Sample Failure</th></tr></thead><tbody>"
    var count = 1;
    for (test_key in scores) {
        if (test_key == "overall_score")
            continue
        breakdown += "<tr><td>" + count++ + "</td>"
        let fail_hash = scores[test_key]["failure_stats"]
        breakdown += "<td>" + fail_hash["num_tests"] + "</td>" +
            "<td>" + fail_hash["num_failures"] + "</td>" +
            "<td>" + fail_hash["failure_rate"] + "</td>" +
            "<td>" + fail_hash["first_mismatch"] + "</td></tr>"
    }
    breakdown += "</tbody></table></p>"
    collapsible.innerHTML += breakdown
}

function write_breakdown(collapsible, scores) {
    collapsible.innerHTML = ""
    let breakdown = "<p style='text-align:left;margin:20px 0px 20px 0px;' class='lead'>Let's see where you went right and where you went wrong </p>" +
        "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" +
        "<thead><tr><th class='topline scope='col'>Test #</th><th class='topline' scope='col'>Status</th><th class='topline' scope='col'>Input Length</th><th class='topline' scope='col'>Input Type</th><th class='topline' scope='col'>Failure Stats</th></tr></thead><tbody>"
    let count = 1;
    for (test_key in scores) {
        if (test_key == "overall_score")
            continue
        breakdown += "<tr><th scope='row'>" + count++ + "</th>" +
            "<td>" + scores[test_key]["status"] + "</td>" +
            "<td>" + scores[test_key]["input_length"] + "</td>" +
            "<td>" + scores[test_key]["input_type"] + "</td>"
        if (scores[test_key]["failure_stats"] != undefined) {
            for (fail_key in scores[test_key]["failure_stats"]) {
                breakdown += "<td>" + scores[test_key]["failure_stats"][fail_key] + "</td>"
            }
        }
        breakdown += "</tr>"
    }
    breakdown += "</tbody></table></p>"
    collapsible.innerHTML += breakdown
}

function write_comp(collapsible, comp_stats, comp_str) {
    collapsible.innerHTML = ""
    comp_str +=
        "<p style='text-align:left; margin:20px 0px;' class='lead'>Let's see how you match up structurally with the desired solution </p>" +
        "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" +
        "<thead><tr><th class='topline' scope='col'>Your Code</th><th class='topline' scope='col'>Our Code</th></tr></thead><tbody>"
    for (let i = 0; i < comp_stats.length; i++) {
        if (comp_stats[i][0].startsWith("skeleton") || comp_stats[i][0].startsWith("lineno"))
            continue
        comp_str += "<tr><th scope='row'>" + comp_stats[i][0] + "</th>" +
            "<td>" + comp_stats[i][1] + "</td></tr>"
    }
    comp_str += "</tbody></table></p>"
    collapsible.innerHTML += comp_str
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
    // lprof_str +=
    //     "<p style='text-align:left; margin:20px 0px;' class='lead'>Check out the performance of your code in more detail </p>" +
    //     "<table style='align:left;max-width:80%;margin-left:auto;margin-right:auto;' class='table table-dark'>" +
    //     "<thead><tr><th class='topline' scope='col'>Line #</th><th class='topline' scope='col'># Hits</th><th class='topline' scope='col'>% Time</th><th class='topline' scope='col'>Real Time</th><th class='topline' scope='col'>Contents</th></tr></thead>"

    // for (fdef in fdefs) {
    //     lprof_str += "<tbody>"
    //     count = 1
    //     lprof_dict = fdefs[fdef]["line_profile"]
    //     for (lprof in lprof_dict) {
    //         hits = lprof_dict[lprof]["hits"]
    //         p_time = parseFloat(lprof_dict[lprof]["%time"])
    //         contents = lprof_dict[lprof]["contents"]
    //         real_time = lprof_dict[lprof]["real_time"] === undefined ? 0 : lprof_dict[lprof]["real_time"];
    //         let bar_colour = p_time < 15 ? (p_time < 10 ? "green" : "orange") : "red";
    //         lprof_str += "<tr><th scope='row'>" + count++ + "</th>" +
    //             "<td style='height:5px;colour:" + bar_colour + ";'>" + hits + "</td>" +
    //             "<td style='height:5px;colour:" + bar_colour + ";'>" + p_time + "</td>" +
    //             "<td style='height:5px;colour:" + bar_colour + ";'>" + real_time + "</td>" +
    //             "<td style='height:5px;colour:" + bar_colour + ";'>" + contents + "</td></tr>"
    //     }
    //     lprof_str += "</tbody>"
    // }
    // lprof_str += "</table></p>"
    // collapsible.innerHTML += lprof_str
}



//Editor set up related 
function init_editor() {
    let editor = ace.edit("editor");
    var main_signature = document.getElementById("main_signature").innerHTML

    editor.setValue(main_signature + "\n    ### write your code below...");            ///Setting initial value here to quickly test

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