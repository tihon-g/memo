import React, {useContext, useEffect} from 'react';
import {observer} from 'mobx-react-lite'
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';

import './Sketchbook.css';
import Configuration from "./Configuration";
import {SketchbookContext} from "../index";
import classNames from "classnames";
import LinearProgress from "@material-ui/core/LinearProgress";


const Sketchbook = observer(({productid}) => {
  const state = useContext(SketchbookContext)

  useEffect(() => {
    state.loadProduct(productid)
    state.openSocket()
  }, [productid])

  const progressClasses = {
    colorPrimary: 'loader__color',
    barColorPrimary: 'loader__bar-color',
    root: 'loader__root'
  }

  return (
    <>
      <div className={'loader'}>
        {state.loadingRender &&
            <LinearProgress color={"primary"} variant={state.progress !== null ? "determinate" : "indeterminate"}
                            value={state.progress * 100} classes={progressClasses}/>
        }
      </div>

      <div className={'product'}>
        <a href={"../"} className={'back-link'}><ChevronLeftIcon />Back to list</a>
        <h2>{state.product.name}</h2>

        <div className={'render'}>
          <div className={'render__container'}>
            <img src={state.image} className={classNames('render__image', state.loadingRender && 'loading')}
                 alt={state.product.name} />

          </div>
        </div>


        <div className={'configuration'}>
          <Configuration />
        </div>
      </div>
    </>
  );
});

export default Sketchbook;
