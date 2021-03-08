let loader = document.getElementById('loader');
let submitbtn = document.getElementById('sub_btn');
let desc = document.getElementById('description'); 

submitbtn.addEventListener('click', function(){
    submitbtn.style.display = 'none';
    desc.style.display = 'none';
    loader.style.display = 'block';
});
