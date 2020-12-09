import * as THREE from './libs/three.module.js';
// управление камерой
import { OrbitControls }  from '../jsm/controls/OrbitControls.js';
import { GUI } from './libs/dat.gui.module.js';


export var gui = new GUI();

export function buildGUI() {

    gui = new GUI( { width: 330 } );
    //gui.domElement.parentElement.style.zIndex = 101;

    var sceneCtrl = gui.add( state, 'scene', Object.keys( scenes ) );
    sceneCtrl.onChange( reload );

    var animCtrl = gui.add( state, 'playAnimation' );
    animCtrl.onChange( toggleAnimations );


}

export var controls2 = new function() {
  this.rotationSpeed = 0.00;
}

class MinMaxGUIHelper {
  constructor(obj, minProp, maxProp, minDif) {
    this.obj = obj;
    this.minProp = minProp;
    this.maxProp = maxProp;
    this.minDif = minDif;
  }
  get min() {
    return this.obj[this.minProp];
  }
  set min(v) {
    this.obj[this.minProp] = v;
    this.obj[this.maxProp] = Math.max(this.obj[this.maxProp], v + this.minDif);
  }
  get max() {
    return this.obj[this.maxProp];
  }
  set max(v) {
    this.obj[this.maxProp] = v;
    this.min = this.min;  // это вызовет setter min
  }
}


function makeXYZGUI(gui, vector3, name, onChangeFn) {
  const folder = gui.addFolder(name);
  folder.add(vector3, 'x', -10, 10).onChange(onChangeFn);
  folder.add(vector3, 'y', 0, 10).onChange(onChangeFn);
  folder.add(vector3, 'z', -10, 10).onChange(onChangeFn);
  folder.open();
}




    //const gui = new GUI();
    gui = new GUI();

//    gui.add(camera, 'fov', 1, 180).onChange(updateCamera);
//    const minMaxGUIHelper = new MinMaxGUIHelper(camera, 'near', 'far', 0.1);
//    gui.add(minMaxGUIHelper, 'min', 0.1, 50, 0.1).name('near').onChange(updateCamera);
//    gui.add(minMaxGUIHelper, 'max', 0.1, 50, 0.1).name('far').onChange(updateCamera);
    //gui.addColor(new ColorGUIHelper(light, 'color'), 'value').name('color');
    var model_folder = gui.addFolder("model");

    model_folder.add(state, 'model', Object.keys( models ) ).onChange( reload );
    model_folder.add(state, 'playAnimation').onChange( toggleAnimations );

    makeXYZGUI(gui, light.position, 'position', updateLight);
    gui.add(light, 'intensity', 0, 2, 0.01);
    makeXYZGUI(gui, light.target.position, 'target', updateLight);

    gui.add(controls2, 'rotationSpeed', -10, 10);


