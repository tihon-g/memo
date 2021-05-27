import {makeAutoObservable} from "mobx"
import isEqual from "lodash/isEqual";
import pickBy from "lodash/pickBy";
import cloneDeep from "lodash/cloneDeep";
import {getProduct} from "../api/api";

const WEB_SOCKET_URL = '/ws/sketchbook/';

class SketchbookState {
  productKind = null
  product = {configuration_set: [], productkind_set: []}
  natures = {}
  patterns = {}
  parts = {}
  socket = null
  image = null
  loadingRender = true
  progress = null

  constructor() { makeAutoObservable(this) }



  // COMPUTED VALUES

  get productKinds() {
    return this.product.productkind_set
  }

  get currentProductKind() {
    return this.product.productkind_set.find(kind => kind.id === this.productKind)
  }

  get productKindConfigurations() {
    return this.currentProductKind.configuration_set
  }

  get productKindParts() {
    return this.productKindConfigurations.map(conf => conf.part);
  }

  get productKindDefaultParts() {
    return Object.fromEntries(this.productKindParts.map(part => {
      return [part.name, this.defaultFinish(part.name)]
    }))
  }

  get productKindSelectedParts() {
    const currentKindParts = this.productKindConfigurations.filter(c => c.colorChart === null).map(conf => conf.part.name)
    return pickBy(this.parts, (value, key) => currentKindParts.includes(key) && value !== null)
  }

  get configurations() {
    let configurationsArr = []
    let configurationsObj = {}

    // collecting all configurations, current product kind configurations has priority over others
    if (this.currentProductKind) { configurationsArr.push(...this.currentProductKind.configuration_set) }
    this.productKinds.forEach(kind => configurationsArr.push(...kind.configuration_set))

    // merge configurations with equal part name to implicitly set product kinds, natures are getting stacked
    configurationsArr.forEach(conf => {
      const name = conf.part.name

      if (name in configurationsObj) {
        conf.part.natures.forEach(nature => {
          if (!configurationsObj[name].part.natures.find(n => nature.id === n.id)) {
            configurationsObj[name].part.natures.push(nature)
          }
        })
      }
      else { configurationsObj[name] = cloneDeep(conf) }
    })

    return Object.values(configurationsObj).sort((a, b) => a.part.id - b.part.id)
  }

  get productParts() {
    return this.configurations.map(conf => conf.part);
  }

  get isPartsSelected() {
    // all parts listed in configuration defined and selected
    return isEqual(
      this.productKindConfigurations.filter(c => c.colorChart === null).map(c => c.part.name).sort(),
      Object.entries(this.productKindSelectedParts).map(([key, value]) => key).sort()
    )
  }

  selectedFinish(partName) {
    return this.parts[partName]
  }

  defaultFinish(partName) {
    const conf = this.configurations.find(conf => conf.part.name === partName)
    const finishes = this.finishesForCurrentPartPattern(partName)

    if (finishes.length > 0) {
      let defaultFinish = finishes.find(finish => finish.id === conf.defaultFinish)
      return defaultFinish ? defaultFinish.id : finishes[0].id
    }

    return null
  }

  defaultPattern(partName) {
    const conf = this.configurations.find(conf => conf.part.name === partName)
    const patterns = this.patternsForCurrentPartNature(partName)

    let defaultPattern = patterns.find(pattern => pattern.finishes.find(finish => finish.id === conf.defaultFinish))
    return defaultPattern ? defaultPattern.id : patterns[0].id
  }

  finishesForCurrentPartPattern(partName) {
    const nature = this.nature(partName)

    if (!nature) return []

    const pattern = nature.patterns.find(p => p.id === this.selectedPattern(partName))
    return pattern ? pattern.finishes : []
  }

  patternsForCurrentPartNature(partName) {
    let nature = this.nature(partName)

    return nature ? nature.patterns.filter(pattern => pattern.finishes.length > 0) : []
  }

  selectedPattern(partName) {
    return this.patterns[partName]
  }

  selectedNature(partName) {
    return this.natures[partName]
  }

  part(partName) {
    return this.productParts.find(part => part.name === partName)
  }

  nature(partName) {
    return this.part(partName).natures.find(n => n.id === this.selectedNature(partName))
  }

  finish(partName) {
    return this.nature(partName)
      .patterns.find(pattern => pattern.id === this.selectedPattern(partName))
      .finishes.find(finish => finish.id === this.selectedFinish(partName))
  }



  // ACTIONS

  loadProduct(productID) {
    getProduct(productID).then(res => {
      this.setProduct(res.data)
      this.setProductKind(this.productKinds[0].id)

      this.productParts.forEach(part => this.changeNature(part.name, part.natures[0].id))
    })
  }

  sendOrderUsingWebSocket() {
    const send = () => {
      this.socket.send(JSON.stringify({
        'type': 'get_render',
        'kind': this.productKind,
        'parts': this.productKindSelectedParts
      }))

      this.renderLoading()
    }

    if (this.socket.readyState === 1) { send() }  // OPEN
    if (this.socket.readyState === 0) { this.socket.onopen = send }  // CONNECTING
  }

  changeFinish(partName, selectedFinish) {
    this.parts[partName] = selectedFinish
    this.changeProductKindOnFinishChange(partName, selectedFinish);

    if (this.isPartsSelected) {
      this.sendOrderUsingWebSocket()
    }
  }

  changePattern(partName, selectedPattern) {
    this.patterns[partName] = selectedPattern

    const patternObj = this.patternsForCurrentPartNature(partName).find(pattern => pattern.id === selectedPattern)
    if (patternObj.finishes.length > 0) {
      this.changeFinish(partName, this.defaultFinish(partName))
    }
  }

  changeNature(partName, selectedNature) {
    this.natures[partName] = selectedNature
    this.changeProductKindOnNatureChange(partName, selectedNature)

    const patterns = this.patternsForCurrentPartNature(partName)
    if (patterns.length > 0) {
      this.changePattern(partName, this.defaultPattern(partName))
    }
  }

  changeProductKindOnFinishChange(partName, finish) {
    const productKindsWithPart = this.productKinds.filter(kind => {
      let findedKind = kind.configuration_set.find(conf => conf.part.name === partName)
      return finish !== undefined ? findedKind : !findedKind;
    }).map(kind => kind.id)

    this.changeProductKindFromAvailable(productKindsWithPart)
  }

  changeProductKindOnNatureChange(partName, nature) {
    const productKindsWithNature = this.productKinds.filter(kind => {
      return kind.configuration_set.find(conf => {
        return conf.part.name === partName && conf.part.natures.find(n => n.id === nature)
      })
    }).map(kind => kind.id)

    this.changeProductKindFromAvailable(productKindsWithNature)
  }

  changeProductKindFromAvailable(available) {
    if (!available.includes(this.productKind)) {
      this.productKind = available[0];
      this.parts = Object.assign(this.productKindDefaultParts, this.productKindSelectedParts);
    }
  }

  openSocket() {
    // eslint-disable-next-line no-restricted-globals
    const wsPath = (location.protocol !== 'https:' ? 'ws://' : 'wss://') + window.location.host + WEB_SOCKET_URL;
    const openedSocket = new WebSocket(wsPath)

    openedSocket.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data['type'] === 'render_created') {
        this.renderLoaded(data['event']['render_path'])
      }
      if (data['type'] === 'render_progress') {
        this.renderProgress(data['event']['progress'])
      }
      if (data['type'] === 'render_error') {
        console.error(data['event']['text'])
        this.renderLoaded(this.image)
      }
    }

    this.socket = openedSocket
  }

  renderLoaded(image) {
    this.image = image
    this.loadingRender = false
  }

  renderLoading() {
    this.loadingRender = true
    this.progress = null
  }

  renderProgress(value) {
    this.progress = value
  }

  setProduct(data) {
    this.product = data
  }

  setProductKind(id) {
    this.productKind = id
  }
}

export default SketchbookState;
