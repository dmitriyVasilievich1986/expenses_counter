/**
 * Navbar logout control: removes the `accessToken` cookie and navigates to `/login`.
 * The trigger is hidden when that cookie is absent.
 */
import Typography from '@mui/material/Typography';
import classnames from 'classnames/bind';
import Cookies from 'js-cookie';
import { useNavigate } from 'react-router';

import * as defaultStyle from './style.scss';

const cx = classnames.bind(defaultStyle);

/**
 * Renders a clickable "Logout" label when an `accessToken` cookie exists; otherwise returns null.
 *
 * @returns {JSX.Element | null} MUI Typography that clears the token and navigates to login, or nothing if logged out.
 */
export function Logout() {
  const navigate = useNavigate();

  /** Removes session cookie and redirects to the login route. */
  const handleLogout = () => {
    Cookies.remove('accessToken');
    navigate('/login');
  };

  if (!Cookies.get('accessToken')) {
    return null;
  }
  return (
    <Typography variant="h6" onClick={handleLogout} className={cx('navlink-text')}>
      Logout
    </Typography>
  );
}
