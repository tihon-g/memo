import React from 'react';
import PropTypes from 'prop-types';
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import classNames from "classnames";

const Select = ({value, onChange, children, className}) => {
  return (
    <div className={classNames('sketchbook-select', className)}>
      <select value={value} onChange={(event) => onChange(event.target.value)}
                    className={'sketchbook-select__input'}>
        {children}
      </select>
      <ExpandMoreIcon className={'sketchbook-select__arrow'}/>
    </div>
  );
};

Select.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  children: PropTypes.node,
  classNames: PropTypes.string,
};

export default Select;
