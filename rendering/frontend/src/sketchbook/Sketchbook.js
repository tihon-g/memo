import React, {useContext, useEffect} from 'react';
import {observer} from 'mobx-react-lite'
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';

import './Sketchbook.css';
import Configuration from "./Configuration";
import {SketchbookContext} from "../index";
import classNames from "classnames";
import Select from "./Select";

const Sketchbook = observer(({productid}) => {
  const state = useContext(SketchbookContext)

  useEffect(() => {
    state.loadProduct(productid)
    state.openSocket()
  }, [productid])

  useEffect(() => {
    state.loadProductKindConfigurations()
  }, [state.productKind])

  return (
    <div className={'product'}>
      <a href={"../"} className={'back-link'}><ChevronLeftIcon />Back to list</a>
      <h2>{state.product.name}</h2>

      <img src={state.image} className={classNames('render__image', state.loadingRender && 'loading')}
           alt={state.product.name} />

      <div className={'configuration'}>
        {state.product.productkind_set.length > 1 &&
          <>
            <h5>Kind</h5>
            <Select value={state.productKind} onChange={(value) => state.productKind = value} className={'mb-md'}>
              {state.product.productkind_set.map(item => (
                <option value={item.id} key={item.id}>{item.name}</option>
              ))}
            </Select>
          </>
        }

        <Configuration />
      </div>
    </div>
  );
});

export default Sketchbook;
