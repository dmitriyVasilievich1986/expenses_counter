import StorefrontIcon from '@mui/icons-material/Storefront';
import { default as MuiCard } from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import classnames from 'classnames/bind';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Card(props: {
  title: string;
  description?: string | null;
  icon?: string | null;
  onClick?: () => void;
  isSelected?: boolean;
}) {
  return (
    <MuiCard className={cx('card', { selected: props.isSelected })} onClick={props.onClick}>
      <CardHeader
        avatar={
          props.icon ? (
            <img src={props.icon} style={{ width: '30px', height: '30px' }} />
          ) : (
            <StorefrontIcon />
          )
        }
        sx={{ overflow: 'hidden' }}
        slotProps={{
          title: {
            variant: 'h6',
            gutterBottom: true,
            sx: {
              textOverflow: 'ellipsis',
              overflow: 'hidden',
              whiteSpace: 'nowrap',
            },
          },
          subheader: { variant: 'caption' },
        }}
        title={props.title}
        subheader={props.description}
      />
    </MuiCard>
  );
}
