import AppBar from '@mui/material/AppBar';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { Link } from 'react-router';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

export function Navbar() {
  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Stack direction="row" spacing={2}>
            <Link to="/" className={cx('navlink-text')}>
              <Typography variant="h6">Home</Typography>
            </Link>
            <Link to="/shop" className={cx('navlink-text')}>
              <Typography variant="h6">Shops</Typography>
            </Link>
          </Stack>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
