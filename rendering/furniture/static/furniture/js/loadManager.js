import * as THREE from './libs/three.module.js';

export var loadManager = new THREE.LoadingManager();
//export var loadManagerObjectName='texture';//texture or model

var loadStartTime, loadedItemsTotal;
var progressBar = document.getElementById('scene-process-progress-bar');
var status = document.getElementById('scene-process-status');

loadManager.onLoad = () => {
  document.getElementById('scene-process-progress').hidden = true;
  let loadtime = ( performance.now() - loadStartTime ).toFixed( 1 ) + ' ms.'
  let msg =  "" + loadedItemsTotal + " objects loaded during: " + loadtime
  status.innerHTML=msg;
  console.log(msg);
};

loadManager.onStart = function ( url, itemsLoaded, itemsTotal ) {
    loadStartTime = performance.now();
    loadedItemsTotal = itemsTotal;
    status.innerHTML="Loading...";
	//console.log( 'Started loading file: ' + url + '.\nLoaded ' + itemsLoaded + ' of ' + itemsTotal + ' files.' );
};

loadManager.onProgress = (urlOfLastItemLoaded, itemsLoaded, itemsTotal) => {
    progressBar.setAttribute('aria-valuemax', itemsTotal);
    progressBar.setAttribute('aria-valuenow', itemsLoaded);
    let percent = Math.floor(itemsLoaded*100/itemsTotal);
    progressBar.setAttribute('style','width:'+Number(percent)+'%');
    loadedItemsTotal = itemsTotal;
    //console.log( '>>Loaded ' + itemsLoaded + ' of ' + itemsTotal + ' files.' );
};

