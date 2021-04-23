let desc = document.getElementById('description'); 
let result_section = document.getElementById('result');
let overall = document.getElementById('overall_score');
let back = document.getElementById('go_back');

function reset(){
    //submitbtn.style.display = 'block';
    desc.style.display = 'block';
    back.style.display = 'none';
    result_section.style.display = 'none';
    overall.style.display = 'none';
}

back.addEventListener('click', reset);