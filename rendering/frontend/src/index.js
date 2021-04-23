import React from 'react';
import ReactDOM from 'react-dom';
import {createContext} from "react";

import './index.css';
import Sketchbook from './sketchbook/Sketchbook';
import SketchbookState from "./sketchbook/SketchbookState";

export const SketchbookContext = createContext(null);

const sketchbook_el = document.getElementById('sketchbook');
ReactDOM.render(
  <SketchbookContext.Provider value={new SketchbookState()}>
    <Sketchbook {...sketchbook_el.dataset} />
  </SketchbookContext.Provider>, sketchbook_el);
