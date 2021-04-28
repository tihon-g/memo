import React, {useState} from 'react';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

export const AccordionItem = ({ label, active, isCollapsed, handleClick, children }) => {
  return (
    <>
      <div className="accordion-header" onClick={handleClick}>
        {active ? <span className={'accordion-header__label-active'}>{label}</span> : <>{label}</>}
        {isCollapsed ? <ChevronLeftIcon /> : <ExpandMoreIcon />}
      </div>
      <div
        className={`accordion-item ${isCollapsed ? 'collapsed' : 'expanded'}`}
        aria-expanded={isCollapsed}
      >
        {children}
      </div>
    </>
  );
};

export const Accordion = ({ defaultIndex, onItemClick, children }) => {
  const [bindIndex, setBindIndex] = useState(defaultIndex);

  const changeItem = itemIndex => {
    if (typeof onItemClick === 'function') onItemClick(itemIndex);
    if (itemIndex !== bindIndex) setBindIndex(itemIndex);
    if (itemIndex === bindIndex) setBindIndex(null);
  };
  const items = children.filter(item => item.type.name === 'AccordionItem');

  return (
    <>
      {items.map(({ props }) => (
        <AccordionItem
          {...props}
          isCollapsed={bindIndex !== props.index}
          handleClick={() => changeItem(props.index)}
          key={props.index}
        />
      ))}
    </>
  );
};
