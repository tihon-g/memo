import {makeAutoObservable} from "mobx"
import isEqual from "lodash/isEqual";
import {getProduct, getProductKindConfiguration} from "../api/api";

class SketchbookState {
  productKind = null
  product = {name: '', swatch: '', productkind_set: []}
  configurations = []
  parts = {}
  socket = null
  image = null
  loadingRender = false

  constructor() {
    makeAutoObservable(this);
  }

  get isPartsSelected() {
    // all parts listed in configuration defined and selected
    return isEqual(this.configurations.filter(c => c.colorChart === null).map(c => c.part.name).sort(), Object.keys(this.parts).sort())
  }

  loadProduct(productID) {
    getProduct(productID).then(res => {
      this.product = res.data
      this.productKind = res.data.productkind_set[0].id
      this.image = res.data.swatch
    })
  }

  loadProductKindConfigurations() {
    if (this.productKind) {
      this.parts = {}
      this.configurations = []

      getProductKindConfiguration(this.productKind).then(res => {
        this.configurations = res.data

      })
    }
  }

  changeFinish(name, finish) {
    this.parts[name] = finish

    if (this.socket.readyState === 1 && this.isPartsSelected && !this.loadingRender) {
      this.socket.send(JSON.stringify({'type': 'get_render', 'kind': this.productKind, 'parts': this.parts}))
      this.loadingRender = true
    }
  }

  openSocket() {
    // eslint-disable-next-line no-restricted-globals
    const wsPath = (location.protocol !== 'https:' ? 'ws://' : 'wss://') + window.location.host + '/ws/sketchbook/';
    const openedSocket = new WebSocket(wsPath)

    openedSocket.onmessage = (e) => {
      const data = JSON.parse(e.data)
      this.image = data['event']['render_path']
      this.loadingRender = false
    }

    this.socket = openedSocket
  }
}

export default SketchbookState;
