import * as THREE from './libs/three.module.js';
import { renderer } from './3.js';
import { loadManager } from './loadManager.js';

export var materialsLib = {}

const loader = new THREE.TextureLoader(loadManager);

function onLoadTexture(texture){
    texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
    texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    //texture.repeat : Vector2
}

function initMaterials(){
    var textures = document.getElementById('finishes').getElementsByTagName('div');
    document.getElementById('scene-process-progress').hidden = false;
    for (let i=0;i<textures.length;i++){
        let tx_id = parseInt(textures[i].getAttribute('tx_id'));
        let diffuse=textures[i].getAttribute('diffuse');
        let props = { name: textures[i].innerHTML};
        if (props['name']=='none') props.visible = false;

        ['metalness', 'roughness'].forEach( //p=> if (textures[i].hasAttribute(p)) props[p]=parseFloat(textures[i].getAttribute(p)));
            function (p) { if(textures[i].hasAttribute(p)) props[p]=parseFloat(textures[i].getAttribute(p));}
            );
        if (!(diffuse===null) && diffuse.slice(-3)=='jpg'){
            // texture Material
           props['map'] = loader.load(diffuse, onLoadTexture);
           if (textures[i].hasAttribute('normal'))
               props['normalMap'] = loader.load(textures[i].getAttribute('normal'), onLoadTexture);
           if (textures[i].hasAttribute('specular').length)
               props['specularMap'] = loader.load(textures[i].getAttribute('specular'), onLoadTexture);
           materialsLib[tx_id] = new THREE.MeshStandardMaterial( props );
        }
        else{
            if (textures[i].hasAttribute('color')) props['color']=parseInt(textures[i].getAttribute("color").slice(1), 16);
            if (textures[i].hasAttribute('transparency'))
            {
                props['transparency'] = parseFloat(textures[i].getAttribute('transparency'));
                props['transparent'] = true;
                materialsLib[tx_id] = new THREE.MeshPhysicalMaterial( props );
            }
            else{
                materialsLib[tx_id] = new THREE.MeshStandardMaterial( props );
            }
        }
    }
    console.log("initMaterials", Object.keys(materialsLib).length );
}

initMaterials();
