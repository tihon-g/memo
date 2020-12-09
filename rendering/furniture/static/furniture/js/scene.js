import * as THREE from './libs/three.module.js';
import { GLTFLoader } from '../jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from '../jsm/loaders/DRACOLoader.js';
import { RGBELoader } from '../jsm/loaders/RGBELoader.js';

// управление камерой
import { OrbitControls }  from '../jsm/controls/OrbitControls.js';
import { GUI } from './libs/dat.gui.module.js';
import { materialsLib} from './material.js';
import { loadManager } from './loadManager.js';

var camera, scene, controls, ratio = 5/4;
export var renderer = new THREE.WebGLRenderer( { antialias: true, alpha: true } );
var pmremGenerator, envMap
var clock = new THREE.Clock();
var canvas;
var panels;
var models = {}; //  model_id => gltf
var modelIDs = {}; // panel_index => model_id

//var loader, mixer, axes;

var timer = Date.now();

var textures_dir, models_dir;
// model loader
var loader = new GLTFLoader(loadManager);
loader.setDRACOLoader( new DRACOLoader().setDecoderPath( '/static/furniture/jsm/loaders/draco/gltf/' ) );

const startParams = {
    //camera_fov : 45,
    camera_pos : new THREE.Vector3(0, 3, 10),
    camera_lookAt : new THREE.Vector3(0, 0.5, 0),
};
var params = {
    camera_pos : new THREE.Vector3(0, 0, 0),
    camera_lookAt : new THREE.Vector3(0, 0, 0),
    };

//var textures_dir = "/static/material/textures/"
var models_dir = "/static/furniture/models/gltf/"

export function init(canvas_name) {

    canvas = document.getElementById( canvas_name );
    // renderer and canvas (outside )
    renderer.setPixelRatio(ratio)
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.setSize(canvas.offsetWidth, canvas.offsetWidth / ratio);

    pmremGenerator = new THREE.PMREMGenerator( renderer );
    pmremGenerator.compileEquirectangularShader();

    canvas.appendChild( renderer.domElement );
    //renderer.setClearColorHex( 0xf0f0f0, 1 );
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera( 40, ratio , 1, 100 );
    //camera.aspect = ratio;
    //focal_length = 50;
    console.log('camera', camera.getFilmHeight(), camera.getFocalLength(), Math.atan( (camera.getFilmHeight()/2) / camera.getFocalLength()) * 180 / Math.PI);
    // https://www.ni.com/ru-ru/support/documentation/supplemental/18/calculating-camera-sensor-resolution-and-lens-focal-length.html

    //camera.up = new THREE.Vector3(0, 1, 0);
    //console.log("scene.position", scene.position)

    var ground = new THREE.Mesh(
        new THREE.PlaneBufferGeometry(12, 12 ),
        new THREE.MeshBasicMaterial( { color: 0x6e6a62, depthWrite: false } )
        //new THREE.MeshBasicMaterial({map: new THREE.TextureLoader().load('static/material/textures/wood/maps/WNP Navy Painted diffuse.jpg')}),
    );
    //надо повернуть землю потому что плоскости по умолчанию смотрят на нас z=0, а нам надо y=0
    ground.rotation.x = - Math.PI / 2; // поэтому крутим ее относительно x
    ground.renderOrder = 1;
    ground.name="myGround";
    scene.add( ground );

    var grid = new THREE.GridHelper( 24, 4, 0x000000, 0x000000 );
    grid.material.opacity = 0.1;
    grid.material.depthWrite = false;
    grid.material.transparent = true;
    scene.add( grid );

    onSceneResetView();
    initGUI(canvas_name);
    updateCamera();
    // ********* connect js to form by adding event callbacks **************
    //MatSelect.addEventListener( 'change', updateMaterials );
    panels =  document.getElementById('panel-models').getElementsByClassName('tab-pane');

    document.getElementById('scene-load-all').onclick = onSceneLoadAll;
    document.getElementById('color-meshes').onclick = onColorMeshes;
    document.getElementById('scene-reset-view').onclick = onSceneResetView;
    document.getElementById('scene-render').onclick = onSceneRender;

    document.getElementById('scene-hdr-select').onchange=onHDRChanged;
    for (let k=0; k < panels.length; k++){
        document.getElementById("nav-model-" + k).onclick = onNavModel;
        panels[k].getElementsByTagName('img')[0].onclick = onTapModelImg; // set best view
        document.getElementById('model-' + k +'-loaded').onchange = onLoadModelStart;
        document.getElementById('model-' + k +'-pos-x').onchange = onChangeModelPos;
        document.getElementById('model-' + k +'-pos-z').onchange = onChangeModelPos;
        document.getElementById('model-' + k +'-rot-y').onclick = onClickModelRot;
        document.getElementById('model-' + k +'-angle').onchange = onChangeModelAng;
        let parts = document.getElementById('contents-' + k).getElementsByClassName("d-flex flex-row");
        for (let i=0;i<parts.length;i++){
            parts[i].getElementsByClassName("form-check")[0].onchange = onShowMeshChange;
            parts[i].getElementsByClassName("custom-select")[0].onchange = onPatternChange;
            parts[i].getElementsByClassName("custom-select")[1].onchange = onFinishChange;

             // todo pattern/finish select
            }
        }
    //updateMaterials();
}



//params = JSON.parse(JSON.stringify(startParams));
//Object.keys(startParams).forEach(p => params[p]=startParams[p]);

//function cameraLookAt(p){
//    params['camera_lookAt']=p;
//    updateCamera();
////    camera.lookAt(params['camera_lookAt']);
////    document.getElementById("camera-lookat").value=params['camera_lookAt'].x+'|'+params['camera_lookAt'].y+'|'+params['camera_lookAt'].z
////    camera.updateProjectionMatrix();
////    render();
//}

function updateCamera(){
    //camera.fov=params['camera_fov'];
    //camera.position.set(params['camera_pos']);
    camera.position.set(params['camera_pos'].x, params['camera_pos'].y, params['camera_pos'].z)
    camera.lookAt(params['camera_lookAt']);
    document.getElementById("camera-pos"   ).value=params['camera_pos'].x   +'|'+(-params['camera_pos'].z)   +'|'+params['camera_pos'].y
    document.getElementById("camera-lookat").value=params['camera_lookAt'].x+'|'+(-params['camera_lookAt'].z)+'|'+params['camera_lookAt'].y
    //document.getElementById("camera-fov").value=params['camera_fov'];
    camera.updateProjectionMatrix();
    render();
}

function initGUI(canvas){
    var gui = new GUI({ autoPlace: true });
    //gui.add(params, 'camera_fov', 25, 90).step(1).onChange(updateCamera);
    const gui_camera_Pos = gui.addFolder('camera position: (z to user, y: up/down)');
    gui_camera_Pos.add( params['camera_pos'], 'x', -6, 6 ).listen().step(0.01).onChange(updateCamera);
    gui_camera_Pos.add( params['camera_pos'], 'z', 0, 15 ).listen().step(0.05).onChange(updateCamera);
    gui_camera_Pos.add( params['camera_pos'], 'y', 0, 6 ).listen().step(0.01).onChange(updateCamera);

    const gui_camera_LookAt = gui.addFolder('camera LookAt (z to user, y: up/down)');
    gui_camera_LookAt.add( params['camera_lookAt'], 'x', -6, 6 ).listen().step(0.5).onChange(updateCamera);
    gui_camera_LookAt.add( params['camera_lookAt'], 'z', -2, 2 ).listen().step(0.05).onChange(updateCamera);
    gui_camera_LookAt.add( params['camera_lookAt'], 'y',  0, 4 ).listen().step(0.01).onChange(updateCamera);

}

//set materials to the current values of the selection menus
function updateMaterials(model_ind, part_name, mat_id) {
    if (model_ind in modelIDs){
        console.log(materialsLib[mat_id],mat_id,part_name)
        models[modelIDs[model_ind]].getObjectByName( part_name ).material = materialsLib[mat_id];
        render();
        }
    else console.log("not loaded " + model_ind + ' ' + part_name);
}

function load_GLB_model(ind, model_id, modelPath) { // put result into fModel

    var fModel;
    let modelName = modelPath.split("/").pop().slice(0,-4);

    if (model_id in models){
        console.log("already loaded!");
        return;
    }
    console.info( `Load ${modelName} started` );

    // loading
    var loadStartTime = performance.now();
    loader.load( modelPath, function ( gltf ) {
        let obj = gltf.scene;
        // bad way for measure time loadStartTime changed from another loading
        console.info( `Load ${modelName} time: ${( performance.now() - loadStartTime ).toFixed( 2 ) } ms.` );
        console.log("gltf.scene", obj, obj.children.length);
        //fModel = gltf.scene;
        if ( obj.children.length == 1){
            //console.log('obj.children.length == 1')
            fModel = obj.children[0]; // ferrari
            }
        else{
            console.log('gltf.scene.children.length >1 ')
            fModel = new THREE.Object3D();
            for (let j = obj.children.length-1; j>=0; j--){
                let p = obj.children[j];
                if (p.name == "Camera") console.log("camera in the model", p);
                else if (p.type == "Mesh" && p.name != "Plane" ) fModel.add(p);
            }
        }
        // shadow
        if (modelName == 'ferrari') {
            var texture = new THREE.TextureLoader().load( 'static/furniture/models/gltf/ferrari.shadow.png' );
            var shadow = new THREE.Mesh(
                new THREE.PlaneBufferGeometry( 0.655 * 4, 1.3 * 4 ),
                new THREE.MeshBasicMaterial( {
                    map: texture, opacity: 0.7, transparent: true
                } )
            );
            // тень тоже крутим (
            shadow.name = "shadow"
            shadow.rotation.x = - Math.PI / 2;
            shadow.renderOrder = 2;
            //scene.add(shadow);

            fModel.add( shadow );

        };

        fModel.name = modelName; //models[model].name;
//        // todo check animation
//        mixer = new THREE.AnimationMixer( gltf.scene );
//        console.log(mixer);

        let box = new THREE.Box3().setFromObject(fModel);
// save size
        document.getElementById('model-' + ind +'-size-x').value=(box.max.x-box.min.x).toFixed(1);
        document.getElementById('model-' + ind +'-size-y').value=(box.max.y-box.min.y).toFixed(1);
        document.getElementById('model-' + ind +'-size-z').value=(box.max.z-box.min.z).toFixed(1);

        // allocate model on the scene
        fModel.position.set(2*ind-panels.length+1, 0, 0);
        console.log("xx**", ind, panels.length, modelName)
        document.getElementById('model-' + ind +'-pos-x').value=fModel.position.x;
        document.getElementById('model-' + ind +'-pos-z').value=-fModel.position.z;
        document.getElementById('model-' + ind +'-angle').value=0;
        document.getElementById('model-' + ind +'-pos-x').disabled=false;
        document.getElementById('model-' + ind +'-pos-z').disabled=false;
        document.getElementById('model-' + ind +'-angle').disabled=false;
        document.getElementById('model-' + ind +'-rot-y').disabled=false;

        document.getElementById('label-model-'+ ind).innerHTML='loaded';
        document.getElementById('model-' + ind + '-loaded').checked = true;
        document.getElementById('model-' + ind + '-loaded').disabled = true;

        document.getElementById('model-' + ind +'-show').disabled = false;
        document.getElementById('model-' + ind +'-show').onchange = onLoadModelShow;
        document.getElementById('model-' + ind +'-show').checked = true;

        document.getElementById('scene-render').hidden = false;

        models[model_id] = fModel;
        modelIDs[ind]=model_id;

        scene.add( fModel );
        //updateMaterials();
        render();
        }, //end of onLoad

        function ( xhr ) {
            document.getElementById('label-model-'+ ind).innerHTML=(xhr.loaded / xhr.total * 100) + '% loaded';
	    },

	    function ( err ) {
            document.getElementById('label-model-'+ ind).innerHTML='not loaded: '+ err.message;
	    },

    ); // end of loader.load
}

function animate(){
    requestAnimationFrame( animate );
    updateCamera();
    render();
    if (mixer) {
        var mixerUpdateDelta = clock.getDelta();
        mixer.update( mixerUpdateDelta );
        }
}

function onWindowResize() {
    renderer.setSize(canvas.offsetWidth, canvas.offsetWidth/ratio);
    camera.updateProjectionMatrix();// *********************************
    render();
}

function hdrEnvSet(hdr_name){
    new RGBELoader()
        .setDataType( THREE.UnsignedByteType )
        .setPath( models_dir + '../hdri/' )
        .load( hdr_name, function ( texture ) {

            envMap = pmremGenerator.fromEquirectangular( texture ).texture;
            scene.background = envMap;
            scene.environment = envMap;
            scene.traverse( function ( child ) {
                if ( child.isMesh ) {
                    child.material.envMap = envMap;
                }
            });
            console.log('scene.environment ' + hdr_name + ' set now');
            render();
        });
    //pmremGenerator.compileEquirectangularShader();
}

function onHDRChanged(){
    hdrEnvSet(this.value);
}

function onLoadModelShow(){
    let show = this.checked;
    models[this.parentNode.parentNode.getAttribute('model_id')].traverse( function ( child ) {
        if ( child.isMesh ) child.visible = show;
    });
    render();
    console.log(this.parentNode.parentNode.getAttribute('model_name') + (show ? " showed ": " hidden"));
}

function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}

function onColorMeshes(){
    for (let ind=0; ind<5; ind++){
        if (ind in modelIDs){
            let finishes = document.getElementById("contents-"+ind).getElementsByTagName('select');
            for (let k=0; k<finishes.length; k++){
                if(finishes[k].id.slice(0,6) =='finish'){
                //console.log(finishes[k]);
                //let options = finishes[k].getElementsByTagName('option');
                let sel = getRandomInt(finishes[k].options.length-1)+1;
                finishes[k].options[sel].selected = true;
                let mesh = finishes[k].getAttribute('mesh');
                let mat_id =  finishes[k].options[sel].value;
                models[modelIDs[ind]].getObjectByName( mesh ).material = materialsLib[mat_id];
                }
            }
        }
    }
    render();
}

function onFinishChange(){
    let mp=this.id.slice('pattern-select-'.length-1);
    let mesh_name = this.getAttribute('mesh');
    let model_ind = parseInt(mp.slice(0,-2));
    //let mat_id = parseInt(this.options[this.selectedIndex].value);
    let mat_id = parseInt(this.options[this.selectedIndex].value);
    if (!(mat_id in materialsLib)){
        console.log('onFinishChange mat trouble', mat_id);
        return;
    }
    console.log('onFinishChange', mesh_name, mat_id, models[modelIDs[model_ind]]);
    updateMaterials(model_ind, mesh_name, mat_id);
}

function onPatternChange(){
    let pattern_id = this.value;
    let options = document.getElementById(this.getAttribute('for')).getElementsByTagName('option');
    console.log('onPatternChange'+ pattern_id + ' ' +options.length);
    for (let i=0; i<options.length; i++){
        console.log(options[i].getAttribute('pattern_id'));
        options[i].hidden = (pattern_id) ? (pattern_id != options[i].getAttribute('pattern_id')) : false;
        }
}

function onShowMeshChange(){
    let mesh_elem = this.parentNode;
    let model_id = parseInt(mesh_elem.getAttribute('model_id'));
    let mesh_name = mesh_elem.getAttribute('mesh');
    models[model_id].getObjectByName( mesh_name ).visible = this.children[0].checked;
    render();
}


function onLoadModelStart(){
    //this.disabled = true;
    loadModelOnPanel(this.parentNode.parentNode);
}

function loadModelOnPanel(panel){
    let m_id = parseInt(panel.getAttribute('model_id'));
    let ind = parseInt(panel.getAttribute('index'));
    let m_name = panel.getAttribute('model_name');
    if (!(ind in modelIDs))
    // todo use model.glb
        load_GLB_model(ind, m_id, models_dir + m_name +".glb"); //async
    else
        console.log(m_name + " already loaded");
}


function onNavModel(){
    let ind = parseInt(this.getAttribute('id').slice('nav-model-'.length));
    if (ind in modelIDs){
        let model_id = modelIDs[ind];
        params['camera_lookAt'].x=models[model_id].position.x;
        params['camera_lookAt'].y=models[model_id].position.y;
        params['camera_lookAt'].z=models[model_id].position.z;
        updateCamera();
        //cameraLookAt(models[model_id].position);
        //render();
        console.log('look at' + models[model_id].position);
    }
}

function onChangeModelPos(){
     let ind=parseInt(this.id.slice('model-'.length,-'-pos-X'.length));
     let dimension=this.id.slice(-1);
     if (ind in modelIDs){
        let val = parseInt(this.value);
        if (!isNaN(val)){
            if (dimension=='z') val = -val;
            models[modelIDs[ind]].position[dimension] = val;
            render();
        }
        else this.value = "0";
     }
}
function onChangeModelAng(){
     let ind=parseInt(this.id.slice('model-'.length,-'-angle'.length));
     if (ind in modelIDs){
        let val = parseFloat(this.value);
        if (!isNaN(val)){
            models[modelIDs[ind]].setRotationFromAxisAngle(new THREE.Vector3(0,1,0), Math.PI/180*val);
            render();
        }
        else this.value=0;
     }
}

function onClickModelRot(){
    let ind=parseInt(this.id.slice('model-'.length,-'-rot-y'.length));
    if (ind in modelIDs){
        if ( this.innerHTML.indexOf('rotate!')>=0 ){
            this.getElementsByTagName('span')[0].hidden=false;
            this.className=this.className.replace('primary', 'danger');
            this.innerHTML = this.innerHTML.split('rotate!').join('stop');
            //models[modelIDs[ind]].rotation.y = Math.PI / 180;
            let timerid = setInterval(() => rotateModel(ind), 60);
            this.setAttribute('timer_id', timerid);
            //this.innerHTML = this.innerHTML.split('primary').join('danger');
            }
        else{
            this.getElementsByTagName('span')[0].hidden=true;
            this.innerHTML = this.innerHTML.split('stop').join('rotate!');
            this.className=this.className.replace('danger', 'primary');
            //models[modelIDs[ind]].rotation.y = 0;
            clearInterval(this.getAttribute('timer_id'))
        }
    }
}

function rotateModel(ind){
    let elem = document.getElementById('model-' + ind +'-angle');
    let val = (parseInt(elem.value) + 1) % 360;
    elem.value = val;
    models[modelIDs[ind]].setRotationFromAxisAngle(new THREE.Vector3(0,1,0), Math.PI/180*val);
    render();
}
// set best View
function onTapModelImg(){
    let ind = parseInt(this.parentNode.getAttribute('index'))
    if (ind in modelIDs){
        console.log(ind, document.getElementById("model-" + ind + "-size-y"));
        let h = parseFloat(document.getElementById("model-" + ind + "-size-y").value);
        let depth = parseFloat(document.getElementById("model-" + ind + "-size-z").value)/2;
        console.log("onTapModelImg", h, depth);
        params['camera_lookAt'].x=parseFloat(document.getElementById("model-" + ind +"-pos-x").value);
        params['camera_lookAt'].z=parseFloat(document.getElementById("model-" + ind +"-pos-z").value);
        params['camera_lookAt'].y=h/2;
        params['camera_pos'].z=depth*3 + params['camera_lookAt'].z;
        params['camera_pos'].y=h*1.5;
        params['camera_pos'].x=params['camera_lookAt'].x;
        //gui.updateDisplay();
        updateCamera();
    }
}


function onSceneLoadAll(){
    for (let k=0; k < panels.length; k++) loadModelOnPanel(panels[k]);
}

function onSceneResetView(){
    //Object.keys(startParams).forEach(p => params[p]=startParams[p]);
    //params['camera_fov']=startParams['camera_fov'];
    params['camera_pos'].x=startParams['camera_pos'].x;
    params['camera_pos'].y=startParams['camera_pos'].y;
    params['camera_pos'].z=startParams['camera_pos'].z;
    params['camera_lookAt'].x=startParams['camera_lookAt'].x;
    params['camera_lookAt'].y=startParams['camera_lookAt'].y;
    params['camera_lookAt'].z=startParams['camera_lookAt'].z;

    //params = JSON.parse(JSON.stringify(startParams));
    //initGUI();
    console.log("ResetView", params, startParams);
    updateCamera();
}
function onSceneRender(){
  console.log('onSceneRender');
   let submit = true;
   for (let ind=0;ind<5;ind++){
     if (document.getElementById('model-' + ind +'-show').checked)
        if (!checkModel(ind))
            submit=false;
  }
  if (submit) document.getElementById('form-scene').submit();
};

function checkModel(ind){
    if (ind==5) {event.preventDefault();  alert("I can't render ferrari in blender now. Uncheck it"); return false;}
    return true;
}


function render(){
    renderer.render( scene, camera );
}
