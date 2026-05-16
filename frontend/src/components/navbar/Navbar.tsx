/**
 * Sticky application bar with primary navigation links and optional logout when authenticated.
 */
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import { Link } from 'react-router';

import { Image } from '@components/image';

import { default as defaultImage } from './expenses.svg';
import { Logout } from './logout';
import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Renders the top navigation: Home, Shops, Products, Transactions, plus {@link Logout} on the right.
 *
 * @returns {JSX.Element} MUI AppBar with router links and logout affordance.
 */
export function Navbar() {
  return (
    <AppBar position="sticky">
      <Container maxWidth="xl">
        <Toolbar disableGutters>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              width: '100%',
              alignItems: 'center',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Image src={defaultImage} width={50} height={50} alt="Home" />
              <Stack direction="row" spacing={2}>
                <Link to="/" className={cx('navlink-text')}>
                  <Typography variant="h6">Home</Typography>
                </Link>
                <Link to="/transaction" className={cx('navlink-text')}>
                  <Typography variant="h6">Transactions</Typography>
                </Link>
              </Stack>
            </Box>
            <Logout />
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
