import React, {useContext, useEffect, useState} from 'react';
import Palette from "./Palette";
import {SketchbookContext} from "../index";
import {observer} from "mobx-react-lite";
import Select from "./Select";

const Part = observer(({name, natures, optional, defaultFinish}) => {
  const state = useContext(SketchbookContext)

  const [selectedNature, setSelectedNature] = useState(natures[0].id)
  const [selectedFinish, setSelectedFinish] = useState(natures[0].finishes[0].id)

  const nature = natures.find(item => item.id === selectedNature)
  const finishes = nature ? nature.finishes : []

  useEffect(() => {
    if (selectedNature !== 0) {
      setSelectedFinish(natures[0].finishes[0].id)
    }
    else {
      setSelectedFinish(0)
    }
  }, [selectedNature])

  useEffect(() => {
    state.changeFinish(name, selectedFinish)
  }, [selectedFinish])

  return (
    <div>
      {(optional || natures.length > 1) &&
        <div className={'mb-md'}>
          <h5>Material</h5>

          <Select value={selectedNature} onChange={(value) => setSelectedNature(parseInt(value))}>
            {optional && <option value={0}>None</option>}
            {natures.map(item => (
              <option value={item.id} key={item.id}>{item.name}</option>
            ))}
          </Select>
        </div>
      }

      {!!selectedNature && <Palette finishes={finishes} onChange={setSelectedFinish} selected={selectedFinish} />}
    </div>
  );
});

export default Part;
