const chatSocket = new WebSocket(
    'wss://' + window.location.host + ':443/'
);

chatSocket.onopen = function (e) {
        console.log("The connection was setup successfully !", chatSocket);
      };


chatSocket.onclose = function (e) {
        console.log("Something unexpected happened !");
      };


chatSocket.onmessage = function (event) {
    const chatMessages = document.querySelector("#chat");
    const data = JSON.parse(event.data);
    if(data.type === 'chat.message'){
    if (data.event_data.sender == 'OctoGPT') {
    cls_name = "octo-msg";
    } else {
    cls_name = "user-msg"
    };
    let chat_div = document.createElement("div");
    let h5_sender = document.createElement("h5");
    h5_sender.classList.add('message-name')
    h5_sender.innerHTML = data.event_data.sender + ": "
    chat_div.classList.add("message", cls_name)
    chat_div.appendChild(h5_sender);
    chat_div.insertAdjacentHTML("beforeend", " "+data.event_data.message);
    document.querySelector("#message-input").value = "";
    chatMessages.appendChild(chat_div);
    } else if(data.type === 'chat.create'){
    if(data.event_data === 'chat_limit'){
    alert('Лимит чатов достигнут, удалите ненужные чаты или улучшите уровень вашей подписки в личном кабинете')
    };
    } else if(data.type === 'token.limit'){
    alert('Закончились токены, улучшите ваш тарифный план в личном кабинете или дождитесь даты обновления лимита')
    };
};

var new_chat_btn = document.querySelector("#add_new_chat");
new_chat_btn.onclick = function (e) {
    document.querySelector("#chat-name-input").focus();
    console.log('new chat div focused')
    };

var new_chat_input = document.querySelector("#chat-name-input");
var plus_btn = document.querySelector("#ui-plus");
plus_btn.onclick = function(e) {
    let new_chatname = new_chat_input.value;
    if(!(new_chatname)){
    new_chatname = 'Новый чат'
    }
    chatSocket.send(JSON.stringify({
        'type': 'chat.create',
        'event_data': new_chatname,
    }));
    setTimeout(location.reload(), 2000);
};

new_chat_input.onblur = function(e) {
    let new_chatname = new_chat_input.value;
    if(!(new_chatname)){
    new_chatname = 'Новый чат'
    }
    chatSocket.send(JSON.stringify({
        'type': 'chat.create',
        'event_data': new_chatname,
    }));
    setTimeout(location.reload(), 2000);
};


window.onload = function() {
  const chatContainer = document.getElementById('chat');
  chatContainer.scrollTop = chatContainer.scrollHeight;
};

document.querySelector("#send-button").onclick = function (e) {
    let messageInputDom = document.querySelector("#message-input");
    const message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'type': 'chat.message',
        'event_data': {
        'sender':'You',
        'message': message},
    }));
};


function del_chat_notify(form_id, chat_name){
    console.log('>>deletion called for form id, chat:',form_id, chat_name);
    let delform = document.getElementById(form_id);
    console.log('form caught', delform);
    let chatDelete = confirm('Вы хотите удалить чат: '+ chat_name+'?');
    if (chatDelete) {
        delform.submit();
} else {
    alert('Удаление отменено')
};
};

