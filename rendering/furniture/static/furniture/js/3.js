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

var textures_dir, models_dir;
// model loader
var loader = new GLTFLoader(loadManager);
loader.setDRACOLoader( new DRACOLoader().setDecoderPath( '/static/furniture/jsm/loaders/draco/gltf/' ) );

export function init(canvas_name, textures_folder, models_folder ) {
    textures_dir = textures_folder;
    models_dir = models_folder;
    //console.log(textures_folder);
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
    camera = new THREE.PerspectiveCamera( 45, ratio , 0.25, 200 );
    camera.aspect = ratio;
    //camera.up = new THREE.Vector3(0, 1, 0);
    updateCamera();
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


    initGUI(canvas_name);
    // ********* connect js to form by adding event callbacks **************
    //MatSelect.addEventListener( 'change', updateMaterials );
    panels =  document.getElementById('panel-models').getElementsByClassName('tab-pane');

    document.getElementById('scene-load-all').onclick = onSceneLoadAll;
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
            parts[i].getElementsByClassName("custom-select")[0].onchange = onPatternChange;
            parts[i].getElementsByClassName("custom-select")[1].onchange = onFinishChange;
             // todo pattern/finish select
            }
        }
    //updateMaterials();
}

function load_GLB_model(ind, model_id, modelPath) { // put result into fModel

    var fModel;
    let modelName = modelPath.split("/").pop().slice(0,-4);

    if (model_id in models){
        console.log("already loaded!");
        return;
    }

    // loading
    var loadStartTime = performance.now();
    loader.load( modelPath, function ( gltf ) {
        let obj = gltf.scene;
        console.info( 'Load time: ' + ( performance.now() - loadStartTime ).toFixed( 2 ) + ' ms.' );
        console.log("gltf.scene", obj, obj.children.length);
        //fModel = gltf.scene;
        if ( obj.children.length == 1){
            // console.log('obj.children.length == 1')
            fModel = obj.children[0]; // ferrari
            }
        else{
            console.log('gltf.scene.children.length !! ', obj.children.length)
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
        fModel.position.x+=len(models) - 1 - 2*ind;
        console.log("****pos x****", ind, fModel.position.x, modelName);
        document.getElementById('model-' + ind +'-pos-x').value=fModel.position.x;
        document.getElementById('model-' + ind +'-pos-z').value=fModel.position.z;
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
            document.getElementById('label-model-'+ ind).innerHTML='not loaded: '+ err;
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
    camera.updateProjectionMatrix();// *********************************
    renderer.setSize(canvas.offsetWidth, canvas.offsetWidth/ratio)
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


function onLoadModelShow(){
    let show = this.checked;
    models[this.parentNode.parentNode.getAttribute('model_id')].traverse( function ( child ) {
        if ( child.isMesh ) child.visible = show;
    });
    render();
    console.log(this.parentNode.parentNode.getAttribute('model_name') + (show ? " showed " : " hided"));
}

function onFinishChange(){
    let mp=this.id.slice('pattern-select-'.length-1);
    let part_name = this.getAttribute('part');
    let model_ind = parseInt(mp.slice(0,-2));
    //let mat_id = parseInt(this.options[this.selectedIndex].value);
    let mat_id = this.options[this.selectedIndex].value;
    if (!(mat_id in materialsLib)){
        console.log('onFinishChange mat trouble', mat_id);
        return;
    }
    console.log('onFinishChange', models[modelIDs[model_ind]])
    updateMaterials(model_ind, part_name, mat_id);
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


function onLoadModelStart(){
    //this.disabled = true;
    loadModelOnPanel(this.parentNode.parentNode);
}

function loadModelOnPanel(panel){
    let m_id = parseInt(panel.getAttribute('model_id'));
    let ind = parseInt(panel.getAttribute('index'));
    let m_name = panel.getAttribute('model_name')
    if (!(ind in modelIDs))
        // load_GLB_model(ind, m_id, m.glb); // todo get relative filename form glb field
        load_GLB_model(ind, m_id, models_dir + m_name +".glb"); //async
    else
        console.log(m_name + " already loaded");
}


function onNavModel(){
    let ind = parseInt(this.getAttribute('id').slice('nav-model-'.length));
    if (ind in modelIDs){
        let model_id = modelIDs[ind];
        camera.lookAt(models[model_id].position);
        render();
        console.log('look at' + models[model_id].position);
    }
}

function onChangeModelPos(){
     let ind=parseInt(this.id.slice('model-'.length,-'-pos-X'.length));
     let dimension=this.id.slice(-1);
     if (ind in modelIDs){
        let val = parseInt(this.value);
        if (!isNaN(val)){
            models[modelIDs[ind]].position[dimension] = val;
            render();
            console.log(models[modelIDs[ind]].position[dimension]);
            console.log(models[modelIDs[ind]].position.x);
        }
        else this.value = "";
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
        params['camera_lookat_x']=parseFloat(document.getElementById("model-" + ind +"-pos-x").value);
        params['camera_lookat_z']=parseFloat(document.getElementById("model-" + ind +"-pos-z").value);
        params['camera_pos_z']=-depth*3 + params['camera_lookat_z'];
        params['camera_pos_y']=h*1.5;
        params['camera_lookat_y']=h/2;
        updateCamera();
    }
}


function onSceneLoadAll(){
    for (let k=0; k < panels.length; k++) loadModelOnPanel(panels[k]);
}

function onSceneResetView(){
    Object.keys(startParams).forEach(p => params[p]=startParams[p]);
    console.log("ResetView", params, startParams);
    updateCamera();
}
function onSceneRender(){

};

function render(){
    renderer.render( scene, camera );

}
