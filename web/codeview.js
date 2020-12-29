document.addEventListener("DOMContentLoaded", function(event){
    let code_block = document.getElementById("fdef");

    fetch('http://127.0.0.1:5500/quicksort.py')
    .then(response => response.text())
    .then(function(text) {

        let fdef_keys = Object.keys(analysis["fdefs"])
        let line_data = []
        for(let j = 0; j < fdef_keys.length; j++) {
            let line_no_keys = Object.keys(analysis["fdefs"][fdef_keys[j]]["line_profile"])
            for(let z = 0; z < line_no_keys.length; z++) {
                let ld = []
                ld.push(parseInt(line_no_keys[z].split("_")[1]) - 1)
                ld.push(parseFloat(analysis["fdefs"][fdef_keys[j]]["line_profile"][line_no_keys[z]]["hits"]))
                ld.push(parseFloat(analysis["fdefs"][fdef_keys[j]]["line_profile"][line_no_keys[z]]["time"]))
                ld.push(parseFloat(analysis["fdefs"][fdef_keys[j]]["line_profile"][line_no_keys[z]]["%time"]))
                ld.push(line_no_keys[z])
                line_data.push(ld)

            }
        }
        console.log(line_data)
        let lines = text.split("\n")
        for(let i = 0, k = 0; i < lines.length; i++) {
            let bg_colour = "white"
            let line = lines[i].replace(/\s/g, '&nbsp;')
            try {
                if(line_data[k][0] == i){
                    bg_colour = line_data[k][3] < 50 ? (line_data[k][3] < 15 ? "#90ee90": "ffdfbf"): "#ff7f7f"
                    k++
                }
            }
            catch {
                ;
            }
            code_block.innerHTML += "<span style='background-color:" + bg_colour + "'>" + line + "</span><br>"
        }
    })

})



