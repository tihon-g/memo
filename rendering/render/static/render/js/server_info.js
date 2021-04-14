
function ajax_get(url, callback) {
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            console.log('responseText:' + xmlhttp.responseText);
            try {
                var data = JSON.parse(xmlhttp.responseText);
            } catch(err) {
                console.log(err.message + " in " + xmlhttp.responseText);
                return;
            }
            callback(data);
        }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

var div_orders = document.querySelector('#orders');
var div_order_template = document.querySelector('#server-info-order-row');
var orders = {};

function ajax_queue_info(){
  ajax_get('/render/queue/', (data) => {
  // {'kind': order.kind.name, 'running': order.running, 'worker': order.worker.name, 'N': order.N, 'done': order.renders_done}
    // add new orders
    //console.log(`/render/queue/ response: ${JSON.stringify(data)}`)
    for (var oid in data){
      console.log(`queue: ${oid}-${data[oid].done}`);
      if (!(oid in orders)){
      var clone = div_order_template.content.cloneNode(true);
      var row = clone.querySelector('.row');
      row.setAttribute('order', oid);
      var cols = row.querySelectorAll('.data');
      cols[0].textContent = oid;
      cols[1].textContent = data[oid].kind;
      cols[2].textContent = data[oid].worker;
      cols[1].href = data[oid].product_ref;
      row.querySelector('.progress-bar').setAttribute('aria-valuemax', data[oid].N);
      div_orders.appendChild(row);
      orders[oid]=row;
      }
    }
    // update or delete orders
    document.querySelector('div.alert.orders').style.display = (Object.keys(orders).length) ? 'block':'none'; // $(this).find('.hider').attr('style', 'display:block;');
    for (var oid in orders){
      if (!(oid in data)) {
        div_orders.removeChild(orders[oid]);
        delete orders[oid];
      } else {
          var progress = orders[oid].querySelector('.progress-bar');
          progress.setAttribute('aria-valuenow', data[oid].done);
          let percent = Math.floor((data[oid].done*100)/data[oid].N);
          progress.setAttribute('style',`width:${percent}%`);
          progress.innerHTML=`${data[oid].done}/${data[oid].N}`
          var b = orders[oid].querySelector('span.badge');
          if (data[oid].running) {
            b.classList.add('badge-success');
            b.classList.remove('badge-danger');
            b.innerHTML = 'running';
          } else {
            b.classList.remove('badge-success');
            b.classList.add('badge-danger');
            b.innerHTML = 'stopped';
          }

      }
    }
    //        var mx = parseInt(data["samples"]);
    //        cur = parseInt(data["cur_sample"]);
    //        percent = Math.floor(cur*100/mx);
  });
  setTimeout(ajax_queue_info, 5000);
};

ajax_queue_info();

$(document).ready(function(){
    // alert("jquery world")
    // var formData = $("#form")
    // var messageInput = $("#id_message")
    // var chatItems = $('#chat-items')
    var loc = window.location
    var prefix = (loc.protocol == "https:") ? "wss://": "ws://";
    var webSocketEndpoint =  prefix + 'server_info/'; //loc.host + loc.pathname;
    console.log(`webSocketEndpoint = ${webSocketEndpoint}`);
    var socket = new WebSocket(webSocketEndpoint)
    //var socket = new ReconnectingWebSocket(webSocketEndpoint)

    socket.onmessage = function(e){
        console.log('on message', e);
        // alert(e.data)
        var msgData = JSON.parse(e.data);
        console.log(msgData);
        // chatItems.append(`<li>${msgData.msg} via ${msgData.user}</li>`)
    }

    socket.onopen = function(e){
        console.log('on open', e);
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
        console.log('on error', e)
    }
    socket.onclose = function(e){
        console.log('on close', e)
    }

    if (socket.readyState == WebSocket.OPEN) {

    } else if (socket.readyState == WebSocket.CONNECTING){
        console.log("connecting..")
    }

})
