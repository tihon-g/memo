$(document).ready(function(){
    //alert("ws started");
//    var formData = $("#form")
//    var messageInput = $("#id_message")
    var msgItems = $('#msg-items');
    var progress = document.querySelector('#progress-one-render');
    var percent = 0
    //var style = document.querySelector('span.kind').innerHTML;
    //var config = document.querySelector('span.config').innerHTML;
    //var quality = document.querySelector('span.quality').innerHTML;
    var model = document.querySelector('span.model').innerHTML;
    var order_id = document.querySelector('span.order_id').innerHTML;
    var loc = window.location
    var prefix = (loc.protocol == "https:") ? "wss://": "ws://";
    //var suffix = `?style=${style}&config=${config}`;
    var webSocketEndpoint =  prefix + loc.host + loc.pathname;// + suffix;
    console.log(`webSocketEndpoint = ${webSocketEndpoint}`);
    //var socket = new WebSocket(webSocketEndpoint)
    var socket = new ReconnectingWebSocket(webSocketEndpoint)

    socket.onmessage = function(e){
        console.log('on message', e);
        // alert(e.data)
        var msgData = JSON.parse(e.data);
        console.log("get via websocket", msgData);
        if (msgData.msg) msgItems.append(`<li>${msgData.msg}</li>`);
        if (msgData.worker){
            document.querySelector('span.worker').innerHTML = msgData.worker;
        }
        if (msgData.progress){
            let p = msgData.progress.split('/')
            percent=Math.floor((100*parseInt(p[0]))/parseInt(p[1]));
            progress.setAttribute('aria-valuenow', percent);
            progress.setAttribute('style',`width:${percent}%`);
        }
        if (msgData.saved)
            document.querySelector('img').src = '/media/' + msgData.saved;
        if (msgData.ready){
            msgItems.append(`<li>${msgData.ready}</li>`);
        }
    }

    socket.onopen = function(e){
        console.log('on open websocket', e);
        var jsonData = JSON.stringify({order: order_id, model: model});
        msgItems.innerHTML="";
        socket.send(jsonData);
//        formData.submit(function(event){
//            event.preventDefault()
//            var messageText = messageInput.val()
//            console.log(`socket.onopen = ${messageText}`)
//            var jsonData = JSON.stringify({msg: messageText, user:'tihon'})
//            socket.send(jsonData)
//            formData[0].reset()
//        })
    }

    socket.onerror = function(e){
        console.log('on error websocket', e)
    }
    socket.onclose = function(e){
        console.log('on close websocket', e)
    }

    if (socket.readyState == WebSocket.OPEN) {

    } else if (socket.readyState == WebSocket.CONNECTING){
        console.log("websocket connecting...")
    }
})
