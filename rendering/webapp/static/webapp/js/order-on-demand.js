  var progress = document.querySelector('#progress-one-render');
  var percent = 0
  //var span_progress =  document.querySelector('span.progress');
  var span_worker = document.querySelector('span.worker');
  var time = "."
  var oid = document.querySelector('span.order_id').innerHTML;

function barsAnime(){
 ajax_get(`/render/order/${oid}/`, (data) => {
   //time = time + '.';
   //span_progress.innerHTML = time;
   if (data.worker) span_worker.innerHTML=data.worker;
   if (data.done){
   //if (data.url) {
     percent = 100;
     clearInterval(timer);
     //span_progress.innerHTML="Ready!";
     //document.querySelector('img').src = data.url;
     var m = document.querySelector('.file_path');
     document.querySelector('img').src = m.getAttribute('media_root')+m.innerHTML;
   } else if (data.worker && data.running){ // {percent=0; clearInterval(timer); span_progress.innerHTML="failed!";}
     if (percent<80) percent += 10;
     else if (percent<98) percent += 2;
   }
    progress.setAttribute('aria-valuenow', percent);
    progress.setAttribute('style',`width:${percent}%`);
 });
};

var timer = setInterval(barsAnime, 1000);