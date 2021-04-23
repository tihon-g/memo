import React from 'react';
import classNames from 'classnames';

const Palette = ({selected, onChange, finishes}) => {
  return (
    <div className={'palette'}>
      {finishes.map(item =>
        <img src={item.url} onClick={() => onChange(item.id)} key={item.id}
             className={classNames('finish-swatch-img', selected === item.id && 'selected')} />
      )}
    </div>
  );
};

export default Palette;
