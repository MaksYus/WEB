function createPost(body,cb){
    const xhr = new XMLHttpRequest();
    xhr.open("POST","http://127.0.0.1:8000/user/auth");
    xhr.addEventListener('load',() => {
        const response = JSON.parse(xhr.responseText);
        cb(response);
    });

   /* xhr.setRequestHeader('Access-Control-Allow-Origin', '*');
    xhr.setRequestHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    xhr.setRequestHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');*/
    xhr.addEventListener('error',()=>{
        console.log('error');
    });

    xhr.send(JSON.stringify(body));
}

function createGet(cb){
    const xhr = new XMLHttpRequest();
    xhr.open("GET","http://127.0.0.1:8000/users/1");
    xhr.addEventListener('load',() => {
        const response = JSON.parse(xhr.responseText);
        cb(response);
    });
    xhr.setRequestHeader('Access-Control-Allow-Origin', 'http://127.0.0.1:8000');
    xhr.setRequestHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    xhr.setRequestHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');


    xhr.addEventListener('error',()=>{
        console.log('error');
    });
    xhr.send();
}

jQuery(document).ready(function($){

    $('.btn_auth').on('click', function(e){
        var login = document.getElementsByName("auth_email")[0];
        var password = document.getElementsByName("auth_pass")[0];
        const newPost = {
            email : login.value,
            password : password.value
        };
        createPost(newPost,response => {
            console.log(response)
        });
    })

    $('.btn_register').on('click', function(e){
        var login = document.getElementsByName("auth_email")[0];
        var password = document.getElementsByName("auth_pass")[0];
        createGet(response => {
            console.log(response['hashed_password'])});
      })

  });