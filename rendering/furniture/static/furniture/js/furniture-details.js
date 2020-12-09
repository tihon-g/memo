
import * as THREE from '/static/furniture/js/libs/three.module.js';
import { GLTFLoader } from '/static/furniture/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from '/static/furniture/jsm/loaders/DRACOLoader.js';
import { RGBELoader } from '/static/furniture/jsm/loaders/RGBELoader.js';
import { OrbitControls }  from '/static/furniture/jsm/controls/OrbitControls.js';
//import { materialsLib} from '/static/furniture/js/material.js';
//import { loadManager } from '/static/furniture/js/loadManager.js';
var loadManager = new THREE.LoadingManager();
var renderer = new THREE.WebGLRenderer({ alpha: true });
var ratio = 1.25;
var canvas = document.getElementById('gltf');
renderer.setSize(canvas.offsetWidth, canvas.offsetWidth / ratio);
canvas.appendChild( renderer.domElement );

var pmremGenerator, envMap;
var models_dir = '/static/furniture/models/gltf/'
// model loader

var loader = new GLTFLoader(loadManager);
loader.setDRACOLoader( new DRACOLoader().setDecoderPath( '/static/furniture/jsm/loaders/draco/gltf/' ) );

var scene = new THREE.Scene();
    pmremGenerator = new THREE.PMREMGenerator( renderer );
    pmremGenerator.compileEquirectangularShader();

var camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 0.5, 100 );
camera.aspect = ratio;
renderer.setClearColor( 0xffffff, 0);
var controls = new OrbitControls( camera, renderer.domElement );
controls.update(); // must be called after any manual changes to the camera's transform

//let modelPath = '/static/furniture/models/gltf/SG01-T7.glb'
export function init(modelPath){

    loader.load( modelPath, function ( gltf ) {
        let obj = gltf.scene;

        console.log("gltf.scene", obj, obj.children.length);
        var fModel;
        if ( obj.children.length == 1){
            console.log('obj.children.length == 1')
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

        let box = new THREE.Box3().setFromObject(fModel);
        camera.position.set( 0, 1, box.max.z * 2.5);
        camera.lookAt( 0, 0, 0);
        camera.updateProjectionMatrix();
        fModel.position.set(0, -(box.max.y - box.min.y)/2, 0)
        scene.add( fModel );
        animate();
        }, //end of onLoad

        function ( xhr ) {
           // document.getElementById('label-model-'+ ind).innerHTML=(xhr.loaded / xhr.total * 100) + '% loaded';
        },

        function ( err ) {
           alert(err);
        },

    ); // end of loader.load

    hdrEnvSet ('quarry_01_1k.hdr');
    animate();
}

function animate() {
	requestAnimationFrame( animate );
	renderer.render( scene, camera );
}

function hdrEnvSet(hdr_name){
    new RGBELoader()
        .setDataType( THREE.UnsignedByteType )
        .setPath( '/static/furniture/models/hdri/' )
        .load( hdr_name, function ( texture ) {

            envMap = pmremGenerator.fromEquirectangular( texture ).texture;
            //scene.background = envMap;

            scene.environment = envMap;
            scene.traverse( function ( child ) {
                if ( child.isMesh ) {
                    child.material.envMap = envMap;
                }
            });
            console.log('scene.environment ' + hdr_name + ' set now');
            //render();
        });
    //pmremGenerator.compileEquirectangularShader();
}

function onWindowResize() {
    camera.updateProjectionMatrix();// *********************************
    renderer.setSize(canvas.offsetWidth, canvas.offsetWidth/ratio)
    console.log(canvas.offsetWidth);
	renderer.render( scene, camera );
}