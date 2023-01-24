var paramsString = document.location.search;
var searchParams = new URLSearchParams(paramsString);

var Token = searchParams.get("token")

p = document.getElementById('User_Login');
//послать запрос пользователя по токену и получить его
//получить свечки и поставить их
p.innerHTML = 'User: ' + String(Token)

const btn_logout = document.querySelector('.btn_logout')
const btn_add = document.querySelector('.btn_add')
const btn_burn = document.querySelector('.btn_burn')
const btn_unburn = document.querySelector('.btn_unburn')
const btn_rem = document.querySelector('.btn_rem')

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

btn_logout.addEventListener('click',e => {
    const newPost = {
    };
    createPost(newPost,response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            window.location.href = 'index.html';
        }
    },"http://127.0.0.1:8000/user/unlog?token="+Token);
});

btn_add.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input')
    createPost(newPost,response => {
        console.log(response);
        if(response['detail']){
            // not ok
        }
        else{
            // ok
        }
    },"http://127.0.0.1:8000/user/unlog?token="+Token);
});

btn_burn.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input')
    createPost(newPost,response => {
        console.log(response);
        if(response['detail']){
            // not ok
        }
        else{
            // ok
        }
    },"http://127.0.0.1:8000/user/unlog?token="+Token);
});

btn_unburn.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input')
    createPost(newPost,response => {
        console.log(response);
        if(response['detail']){
            // not ok
        }
        else{
            // ok
        }
    },"http://127.0.0.1:8000/user/unlog?token="+Token);
});

btn_rem.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input')
    createPost(newPost,response => {
        console.log(response);
        if(response['detail']){
            // not ok
        }
        else{
            // ok
        }
    },"http://127.0.0.1:8000/user/unlog?token="+Token);
});

//alert(value)