import React from 'react';
import classNames from 'classnames';
import Block from '@material-ui/icons/Block';

const Palette = ({selected, onChange, finishes, showEmpty, isEmpty, onEmptyClick}) => {
  return (
    <div className={'palette'}>
      {showEmpty &&
        <div className={classNames('finish-swatch-img', isEmpty && 'selected', 'finish-swatch-img--empty')}
             onClick={onEmptyClick}>

          <Block fontSize={'large'} />
        </div>
      }

      {finishes.map(item =>
        <img src={item.url} onClick={() => onChange(item.id)} key={item.id}
             className={classNames('finish-swatch-img', selected === item.id && 'selected')} />
      )}
    </div>
  );
};

export default Palette;
