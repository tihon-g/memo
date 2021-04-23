import React, {useState} from 'react';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

export const AccordionItem = ({ label, isCollapsed, handleClick, children }) => {
  return (
    <>
      <div className="accordion-header" onClick={handleClick}>
        {label}
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
  };
  const items = children.filter(item => item.type.name === 'AccordionItem');

  return (
    <>
      {items.map(({ props }) => (
        <AccordionItem
          isCollapsed={bindIndex !== props.index}
          label={props.label}
          handleClick={() => changeItem(props.index)}
          children={props.children}
        />
      ))}
    </>
  );
};
