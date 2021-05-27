import React, {useState} from 'react';
import classNames from "classnames";

export const StepperItem = ({ label, active, isCollapsed, handleClick, children, position }) => {
  const labelClasses = classNames(
    'stepper-item-label',
    active && 'stepper-item-label--active',
    !isCollapsed && 'stepper-item-label--expanded'
  )

  return (
    <>
      <div className={labelClasses} onClick={handleClick}>
        <span>{label}</span>
      </div>
      <div className={`stepper-item ${isCollapsed ? 'collapsed-' + position : 'expanded'}`} aria-expanded={isCollapsed}>
        {children}
      </div>
    </>
  );
};

export const VerticalStepper = ({ defaultIndex, onItemClick, children }) => {
  const [bindIndex, setBindIndex] = useState(defaultIndex);

  const changeItem = itemIndex => {
    if (typeof onItemClick === 'function') onItemClick(itemIndex);
    if (itemIndex !== bindIndex) setBindIndex(itemIndex);
  };

  return (
    <div className={'vertical-stepper'}>
      <div className={'vertical-stepper__divider'} />
      {children.map(({ props }) => (
        <StepperItem
          {...props}
          isCollapsed={bindIndex !== props.index}
          position={bindIndex < props.index ? 'above' : 'below'}
          handleClick={() => changeItem(props.index)}
          key={props.index}
        />
      ))}
    </div>
  );
};

export default VerticalStepper;
