import React from 'react';
import classNames from 'classnames';
import Block from '@material-ui/icons/Block';
import ReactTooltip from "react-tooltip";

const Palette = ({selected, onChange, finishes, showEmpty, isEmpty, onEmptyClick}) => {
  return (
    <div className={'palette'}>
      {showEmpty &&
        <div className={classNames('finish-swatch-img', isEmpty && 'selected', 'finish-swatch-img--empty')}
             onClick={onEmptyClick}>

          <Block fontSize={'large'} />
        </div>
      }

      {finishes.map(item => {
        const tooltipID = 'finish_' + item.id
        return (
          <React.Fragment key={item.id}>
            <img src={item.url} onClick={() => onChange(item.id)} key={item.id} data-tip data-for={tooltipID}
                 className={classNames('finish-swatch-img', selected === item.id && 'selected')} />
            <ReactTooltip id={tooltipID} place="top" type="light" effect="solid" border borderColor={'#dee2e6'}
                          className={'finish-swatch-tooltip'}>
              {item.display_name}
            </ReactTooltip>
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default Palette;
