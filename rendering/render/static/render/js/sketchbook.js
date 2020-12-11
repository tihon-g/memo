
// update controls without any communication with server
// it will be fast
var render_names = [];
var selected = {};
var dict_tx = {}; // dict_tx[tx] = pattern_id
var dict_pt = {}; // dict_pt[pattern_id] = [list textures]
var render_indices = [];
var render_index=0;
var order_url = '';
//var orders;
var parts = {};
var kind;
const media = document.getElementById('media-root').getAttribute('mediaurl');
const anyImg = document.getElementById('media-root').getAttribute("web_img")+'any-img.png';

var root;
var product_id;
var loaded = false;

window.onload = function() {
    root = document.querySelector('#render-images');
    // load finishes to patterns relations
    Array.from(document.querySelector('#patterns').children).forEach(el => {
        const pat = el.getAttribute('pattern_id');
        el.innerHTML.split(',').forEach(f => dict_tx[f]=pat);
    });
//    // save witch kind in order
//    orders = {};
//    Array.from(document.querySelector('#orders-data').children).forEach(el => orders[el.getAttribute('order_id')]=el.getAttribute('kind_id'));

    // colorchart processing
    Array.from(document.querySelectorAll('.colorchart')).forEach(el => {
        el.style.display='none';
        el.querySelector('.finishes-selected').innerHTML=1;
    });

    // different for order/product
    var req;
    if (document.querySelector('form').getAttribute('name')=='productsketchbook'){
        const product_id = root.getAttribute('product');
        req = `/render/product/${product_id}/renders`;
        selectKind(0);// select first kind
         // <- calc_matches();
    } else {
        const order_id = root.getAttribute('order');
        req = `/render/order/${order_id}/renders`;
        kind=0;
    }
    ajax_get(req, (data) => {
       console.log(`ajax_get: ${data.renders}`);
       //render_names = data.renders.map( el => `${el.split('/')[1]}|${el.split('=')[1].split('.')[0]}`);
       render_names = data.renders;
       console.log(`ready product renders: ${render_names.length}`);
       loaded = true;
       calc_matches();
    });

}

function checkPart(){
    const status = event.target.checked;
    const part = event.target.closest(".row")
    part.querySelector('.custom-select.finish').disabled = !status;
    part.querySelector('.custom-select.pattern').disabled = !status;
    const header = part.querySelector(".alert");
    if (status) {
        header.classList.remove("alert-secondary");
        header.classList.add("alert-success");
        //calc_variants(part);
    } else {
        header.classList.remove("alert-success");
        header.classList.add("alert-secondary");
        //part.querySelector("span.finishes-selected").innerHTML = 1;
        part.querySelector("img").src = f_swatch_src(0);
    }
    calc_matches();
    return;
}

function changeQuality(q){
    //alert(q.checked);
}


function p_swatch_src(p_id){
    if (p_id<0) return anyImg;
    return document.getElementById('media-root').getAttribute("swatches_root")+`p${p_id}.jpg` // "0.png"

}
function f_swatch_src(f_id){
    return document.getElementById('media-root').getAttribute("swatches_root") + ((f_id) ? `${f_id}.jpg`: "0.png")
}

function changeProductKind() {
   selectKind( event.target.selectedIndex );
}

function selectKind(ind) {
    console.log("selectKind", ind);
    if (ind<0) return;
    const kind_id = document.querySelector("#kind-selector").options[ind].getAttribute("kind");
    if (kind_id === kind) return;
    if (kind) document.querySelector(`#kind-${kind}`).style.display = 'none';
    let row = document.querySelector(`#kind-${kind_id}`)
    row.style.display = 'block';
    kind = kind_id;
    calc_matches();
}

function calc_variants(part){
    let variants = 1;
    if (!part.classList.contains('colorchart') && part.querySelector('input').checked)
    {
        let f_id = part.querySelector(".custom-select.finish").value;
        if (f_id<0) { // finish is not selected
            part.querySelector("img").src = p_swatch_src(part.querySelector(".custom-select.pattern").value);
            // sum unhidden options - 1(==any) + (1 if optional)
            variants = Array.from(part.querySelector(".custom-select.finish").querySelectorAll('option'))
                .map(el => (el.hidden) ? 0:1)
                .reduce((a, b) => a + b, 0) - 1 + ((part.classList.contains('optional')) ? 1:0);
        } else {
         part.querySelector("img").src = f_swatch_src(f_id);
        }
    }
    part.querySelector("span.finishes-selected").innerHTML = variants;
    return variants
}

function changeFinish(){
    let part = event.target.closest(".row")
    calc_variants(part);
    calc_matches();
}

 function changePattern(){
    console.log("changePattern", event.target);
    let pattern_id = event.target.value;

    let part = event.target.closest(".row")
    let finishes = part.querySelector('.custom-select.finish').getElementsByTagName('option');
    var f_count=0;
    Array.from(finishes).forEach(el => {
        el.hidden = (pattern_id != -1 && pattern_id != el.getAttribute('pattern_id'));
        el.selected = (el.value == -1);
        if (!el.hidden) f_count++;
    });
    if (pattern_id == -1 && part.classList.contains("optional")) f_count++;
    part.querySelector("span.finishes-selected").innerHTML = f_count;
    event.target.closest(".row").querySelector("img").src = p_swatch_src(pattern_id);
    calc_matches();
}

function show_render(val) {
    var src;
    render_index = parseInt(val)-1;
    if (render_index < render_indices.length){
        document.getElementById('show-render-badge').innerHTML=val;
        document.getElementById('render-current').value=val;
        src = media + render_names[render_indices[render_index]];
    } else {
        document.getElementById('show-render-badge').innerHTML='nothing';
        src = '/static/render/img/blender-logo.jpg';
    }
    document.getElementById('nav-renders').hidden = (render_indices.length < 2);
    document.getElementById('render-src').setAttribute('src', src);
}

function next_render(step){//step = +1/-1
    let N = render_indices.length;
    if (N<2) return;
    show_render( ((render_index + parseInt(step) + N) % N)+1 );
}

function calc_matches(){
    if (!loaded) return;
    // multiply variants from all parts
    let row = document.querySelector(`#kind-${kind}`)
    const order = {};
    const order_parts = [];
    const variants = Array.from(row.querySelectorAll("span.finishes-selected"))
        .map(el => calc_variants(el.closest('.row')))
        .reduce((a,b) => a*b, 1);
    document.querySelector("#variants-count").innerHTML = variants;

    const parts = Array.from(row.querySelectorAll(".row.part"));
    parts.forEach(p => {
        var mats="";
        const status = p.querySelector('input').checked;
        const pattern = p.querySelector('.custom-select.pattern').value;
        const finish = p.querySelector('.custom-select.finish').value;
        const meshes = Array.from(p.querySelectorAll("span.mesh")).map(m => m.innerHTML.split('.')[1]);

        if (!status) mats="0";
        else if (pattern == -1 && finish == -1) mats="*";
        else if (finish == -1) mats=`p${pattern}`;
        else mats=`${finish}`;

        meshes.forEach(mesh => order[mesh]=mats);
        if (!p.classList.contains('colorchart')){
            var partname = p.querySelector('span.partname').innerHTML;
            order_parts.push(`${partname}:${mats}`);
        }
        //order_parts.push(`${meshes.join(',')}:${mats}`);

    });
    if (document.querySelector("#order-variants")){
        document.querySelector("#order-variants").innerHTML = variants;
        // calculate order
        document.querySelector(".order.kind").innerHTML = kind;
        document.querySelector("span.order.parts").innerHTML = order_parts.join(';');
    }
    // count renders
    render_indices = [];
    render_names.forEach((f,i) => {
        if (f.split('=')[1].split('.')[0].split('_').every(pm => {
            x = pm.split('-');
            let mesh=x[0];
            let mat=x[1];
            if (!(mesh in order) || order[mesh]=="0") return (mat == "0");
            if (order[mesh]=="*") return true;
            if (!order[mesh].startsWith('p')) return (mat == order[mesh]);
            // check pattern
            return (dict_tx[mat]==order[mesh].substring(1))
        })) render_indices.push(i);
    });
    const renders = render_indices.length;
    document.querySelector('#renders-count').innerHTML=renders;
    document.getElementById('suggested').innerHTML = renders;
    document.getElementById('render-current').setAttribute('max', renders);
    show_render(1);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function order(){
    if (document.querySelector("#order-variants").innerHTML == document.querySelector("#renders-count").innerHTML){
        alert('You have ready all variants! Nothing to do!');
        return;
    }
    if (parseInt(document.querySelector("#order-variants").innerHTML) > 100) {
        alert('too big order request');
        return;
    }
    rule = document.querySelector('span.order.parts').innerHTML;
    const csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax({
        type: "POST",
        url: "/render/order/",
        data: JSON.stringify({ kind: kind, rule: rule, quality: 1 }), // todo quality
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){alert(`A new render order now running ${JSON.stringify(data)}`);},
        error: function(errMsg){alert(`failed  /render/order/: ${JSON.stringify(errMsg)}`);}
    });
}
