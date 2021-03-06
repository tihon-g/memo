import React, {useContext} from 'react';
import Palette from "./Palette";
import {SketchbookContext} from "../index";
import {observer} from "mobx-react-lite";
import Select from "./Select";

const Part = observer(({name, natures, optional, removable}) => {
  const state = useContext(SketchbookContext)

  const onRemovePart = () => {
    if (optional) { state.changeFinish(name, 0) }
    if (removable) { state.changeFinish(name, undefined) }
  }

  const selectedFinish = state.selectedFinish(name)
  const patterns = state.patternsForCurrentPartNature(name)

  return (
    <div className={'part'}>
      {natures.length > 1 &&
        <div className={'mb-sm'}>
          <h5>Material</h5>
          <Select value={state.selectedNature(name)}
                  onChange={(value) => state.changeNature(name, parseInt(value))}>
            {natures.map(item => (
              <option value={item.id} key={item.id}>{item.name}</option>
            ))}
          </Select>
        </div>
      }

      {patterns.length > 1 &&
        <div className={'mb-sm'}>
            <h5>Pattern</h5>
            <Select value={state.selectedPattern(name)}
                    onChange={(value) => state.changePattern(name, parseInt(value))}>
              {patterns.sort((a,b) => (a.name > b.name) ? 1 : -1 ).map(item => (
                <option value={item.id} key={item.id}>{item.display_name}</option>
              ))}
            </Select>
          </div>
      }

      <div className={'current-finish'}>
        {!!state.selectedFinish(name) ? state.finish(name).display_name : <>&nbsp;</>}
      </div>

      {!!state.selectedNature(name) && !!state.selectedPattern(name) &&
        <Palette finishes={state.finishesForCurrentPartPattern(name)}
                 onChange={finish => state.changeFinish(name, finish)}
                 selected={state.selectedFinish(name)}
                 showEmpty={optional || removable}
                 onEmptyClick={onRemovePart}
                 isEmpty={(optional && selectedFinish === 0) || (removable && selectedFinish === undefined)}
      />
      }
    </div>
  );
});

export default Part;
