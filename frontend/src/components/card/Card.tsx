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
            <img src={props.icon} style={{ width: '24px', height: '24px' }} />
          ) : (
            <StorefrontIcon sx={{ fontSize: '24px' }} />
          )
        }
        sx={{
          overflow: 'hidden',
          padding: '8px 12px',
        }}
        slotProps={{
          title: {
            variant: 'body2',
            gutterBottom: false,
            sx: {
              textOverflow: 'ellipsis',
              overflow: 'hidden',
              whiteSpace: 'nowrap',
              lineHeight: 1.3,
              fontSize: '0.875rem',
              fontWeight: 500,
            },
          },
          subheader: {
            variant: 'caption',
            sx: {
              lineHeight: 1.2,
              fontSize: '0.7rem',
            },
          },
        }}
        title={props.title}
        subheader={props.description}
      />
    </MuiCard>
  );
}
