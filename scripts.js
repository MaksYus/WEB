function createPost(body,cb,url){
    const xhr = new XMLHttpRequest();
    xhr.open("POST",url);
    xhr.addEventListener('load',() => {
        const response = JSON.parse(xhr.responseText);
        cb(response);
    });

    xhr.setRequestHeader('access-control-allow-credentials', true);
    xhr.setRequestHeader('access-control-allow-origin', '*');
    xhr.setRequestHeader('content-type', 'application/json');

    xhr.addEventListener('error',()=>{
        console.log('error');
    });
    xhr.send(JSON.stringify(body));
}

function createGet(cb,url){
    const xhr = new XMLHttpRequest();
    xhr.open("GET",url);
    xhr.addEventListener('load',() => {
        const response = JSON.parse(xhr.responseText);
        cb(response);
    });
    xhr.setRequestHeader('access-control-allow-credentials', true);
    xhr.setRequestHeader('access-control-allow-origin', '*');
    xhr.setRequestHeader('content-type', 'application/json');


    xhr.addEventListener('error',()=>{
        console.log('error');
    });
    xhr.send();
}
jQuery(document).ready(function($){

    const btn_auth = document.querySelector('.btn_auth')
    const btn_reg = document.querySelector('.btn_register')

    btn_auth.addEventListener('click',e => {
        var login_ = document.getElementsByName("auth_email")[0];
        var password = document.getElementsByName("auth_pass")[0];
        const newPost = {
            login : login_.value,
            password : password.value
        };
        createPost(newPost,response => {
            console.log(response);
            if(response['detail']){alert(response['detail']);}
            else{
                //alert(response['token'])
                window.location.href = 'main_page.html?token='+response['token'];
            }
        },"http://127.0.0.1:8000/user/auth");
    });

    btn_reg.addEventListener('click',e => {
        var login_ = document.getElementsByName("auth_email")[0];
        var password = document.getElementsByName("auth_pass")[0];
        const newPost = {
            login : login_.value,
            password : password.value
        };
        resp = ''
        createPost(newPost,response => {
            console.log(response)
        },"http://127.0.0.1:8000/user/register");
    });

  });