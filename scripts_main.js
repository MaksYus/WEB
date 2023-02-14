var paramsString = document.location.search;
var searchParams = new URLSearchParams(paramsString);

var Token = searchParams.get("token");

p = document.getElementById('User_Login');
//послать запрос пользователя по токену и получить его
//получить свечки и поставить их


const btn_logout = document.querySelector('.btn_logout');
const btn_add = document.querySelector('.btn_add');
const btn_burn = document.querySelector('.btn_burn');
const btn_unburn = document.querySelector('.btn_unburn');
const btn_rem = document.querySelector('.btn_rem');
const btn_post_message = document.querySelector('.btn_post_mes');

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

user = {};
user_components = {};

function updateChat(){
    messges = [];
    createGet(response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            console.log(response);
            document.getElementById('first_message').innerHTML =response[0].user_id + ' -> ' + response[0].text;
            document.getElementById('second_message').innerHTML =response[1].user_id + ' -> ' + response[1].text;
            document.getElementById('third_message').innerHTML =response[2].user_id + ' -> ' + response[2].text;
            document.getElementById('forth_message').innerHTML =response[3].user_id + ' -> ' + response[3].text;
            document.getElementById('fifth_message').innerHTML =response[4].user_id + ' -> ' + response[4].text;
        }
    },"http://127.0.0.1:8000/chat/get_top_5/");

}
updateChat()
let timerId = setInterval(() => updateChat(), 5*1000);

// инициализация пользователя
createGet(response => {
    console.log(response);
    if(response['detail']){
        alert(String(response['detail']));
    }
    else{
        user = response;
        p.innerHTML = 'User: ' + String(user['login']);
        // инициализация компонент пользователя
        createGet(response2 => {
            console.log(response2);
            if(response2['detail']){
                alert(response2['detail']);
            }
            else{
                user_components = response2['components'];
                console.log(user_components);
            }
        },"http://127.0.0.1:8000/user/components/"+user['id']);

    }
},"http://127.0.0.1:8000/user_by_token/"+Token);




btn_logout.addEventListener('click',e => {
    createGet(response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            window.location.href = 'index.html';
        }
    },"http://127.0.0.1:8000/user/unlog/"+Token);
});

btn_add.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input').value
    const newPost = {'new_candle':{
        'life_time':3600,
        'candle_type_id':1,
        'user_id':user['id']
    },'components':user_components};
    createPost(newPost,response => {
        console.log(response);
        if(response["detail"]){
            alert(response["detail"]);
        }
        else{
            document.getElementById('candle'+wr_id).style.visibility = 'visible';
            document.getElementById('flame'+wr_id).style.visibility = 'visible';
        }
    },"http://127.0.0.1:8000/candle/add_to_user?in_user_int="+wr_id);
});

btn_burn.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input').value
    createGet(response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            createPost(user_components,response2 => {
            console.log(response2);
            if(response2['detail']){
               alert(response2['detail']);
            }
            else{
                document.getElementById('flame'+wr_id).style.visibility = 'visible';
            }
            },"http://127.0.0.1:8000/candle/burn/"+response['id']);
        }
    },"http://127.0.0.1:8000/candle/get_on_pos_in_user?candle_in_user_interface="+wr_id+"&user_id="+user['id']);
});

btn_unburn.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input').value
    createGet(response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            createPost(user_components,response2 => {
            console.log(response2);
            if(response2['detail']){
               alert(response2['detail']);
            }
            else{
                document.getElementById('flame'+wr_id).style.visibility = 'hidden';
            }
            },"http://127.0.0.1:8000/candle/unburn/"+response['id']);
        }
    },"http://127.0.0.1:8000/candle/get_on_pos_in_user?candle_in_user_interface="+wr_id+"&user_id="+user['id']);
});

btn_rem.addEventListener('click',e => {
    wr_id = document.querySelector('.index_input').value

    createGet(response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            createPost(user_components,response2 => {
            console.log(response2);
            if(response2['detail']){
               alert(response2['detail']);
            }
            else{
                document.getElementById('candle'+wr_id).style.visibility = 'hidden';
                document.getElementById('flame'+wr_id).style.visibility = 'hidden';
            }
            },"http://127.0.0.1:8000/candle/remove/"+response['id']);
        }
    },"http://127.0.0.1:8000/candle/get_on_pos_in_user?candle_in_user_interface="+wr_id+"&user_id="+user['id']);

    
});


btn_post_message.addEventListener('click',e => {
    message_text = document.querySelector('.message_input').value

    const message_data = {'data':{
        'text':message_text,
        'user_id':user['id']
    },'components':user_components};

    createPost(message_data,response => {
        console.log(response);
        if(response['detail']){
            alert(response['detail']);
        }
        else{
            updateChat();
        }
    },"http://127.0.0.1:8000/chat/post_message");
});

//alert(value)