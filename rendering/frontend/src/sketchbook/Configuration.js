import React, {useContext} from 'react';
import Part from "./Part";
import {SketchbookContext} from "../index";
import {observer} from "mobx-react-lite";
import {Accordion, AccordionItem} from "./Accordion";

const Configuration = observer((props) => {
  const state = useContext(SketchbookContext)

  return <Accordion>
    {
      state.configurations.filter(conf => conf.colorChart === null).map(conf => (
        <AccordionItem key={conf.part.name}
                       label={conf.part.name}
                       index={conf.part.name}
                       active={!!state.parts[conf.part.name]}>

          <Part {...conf.part} optional={conf.optional} defaultFinish={conf.defaultFinish} removable={conf.removable} />
        </AccordionItem>
      ))
    }
  </Accordion>
});

export default Configuration;
