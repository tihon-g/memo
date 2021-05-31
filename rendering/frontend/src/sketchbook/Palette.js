import React, {useState} from 'react';
import classNames from 'classnames';
import Block from '@material-ui/icons/Block';
import ArrowBackIcon from '@material-ui/icons/ArrowBack';
import ArrowForwardIcon from '@material-ui/icons/ArrowForward';
import ReactTooltip from "react-tooltip";
import chunk from "lodash/chunk";

const PAGE_SIZE = 20;

const Palette = ({selected, onChange, finishes, showEmpty, isEmpty, onEmptyClick}) => {
  const [page, setPage] = useState(0);

  const start = page * PAGE_SIZE;
  const end = start + PAGE_SIZE;

  const items = []

  if (showEmpty) {
    items.push(
      <div className={classNames('finish-swatch-img', isEmpty && 'selected', 'finish-swatch-img--empty')}
           onClick={onEmptyClick}>
        <Block fontSize={'large'} />
      </div>
    )
  }

  items.push(...finishes.map(item => {
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
  }))

  const pages = chunk(items, PAGE_SIZE);

  return (
    <>
      {pages.map((items, i) => (
        <div className={classNames('palette', i !== page && 'hidden')}>
          {items}
        </div>
      ))}
      <div className={'palette-paging'}>
        <div>{page > 0 && <ArrowBackIcon fontSize={'large'} className={'palette-paging--arrow'}
                                         onClick={() => setPage(page-1)} />}</div>
        <div>{items.length > end && <ArrowForwardIcon fontSize={'large'} className={'palette-paging--arrow'}
                                                      onClick={() => setPage(page+1)} />}</div>
      </div>
    </>
  );
};

export default Palette;
