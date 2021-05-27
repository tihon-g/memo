import React, {useContext} from 'react';
import Part from "./Part";
import {SketchbookContext} from "../index";
import {observer} from "mobx-react-lite";
import VerticalStepper, {StepperItem} from "./VerticalStepper";

const Configuration = observer((props) => {
  const state = useContext(SketchbookContext)

  const configurations = state.configurations.filter(conf => conf.colorChart === null)

  if (configurations.length === 0) return <></>

  return <VerticalStepper defaultIndex={0}>
    {configurations.map((conf, index) => (
        <StepperItem key={conf.part.name}
                     label={conf.part.name}
                     index={index}
                     active={!!state.parts[conf.part.name]}>
          <Part {...conf.part} optional={conf.optional} defaultFinish={conf.defaultFinish} removable={conf.removable} />
        </StepperItem>
      ))
    }
  </VerticalStepper>
});

export default Configuration;
