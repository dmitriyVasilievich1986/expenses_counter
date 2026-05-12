import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import dayjs from 'dayjs';
import Cookies from 'js-cookie';
import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router';

import { SubmitButton } from '@components/submitButton';
import { useAuthAPIClient } from '@services/apiClient/auth';

export function Login() {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirectTo = searchParams.get('redirectTo') ?? '/';

  const { login } = useAuthAPIClient();

  const handleSubmit = async () => {
    login(username, password).then((response) => {
      Cookies.set('accessToken', response.accessToken, {
        expires: dayjs(response.expiresAt).toDate(),
      });
      navigate(redirectTo);
    });
  };

  return (
    <Container maxWidth="sm">
      <Paper sx={{ p: 2, mt: 2 }}>
        <form style={{ marginTop: '1rem' }} onSubmit={handleSubmit}>
          <Box sx={{ my: 4 }}>
            <Stack spacing={2}>
              <TextField
                label="Username"
                name="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
              />
              <TextField
                label="Password"
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <SubmitButton label="Login" color="primary" onClick={handleSubmit} />
            </Stack>
          </Box>
        </form>
      </Paper>
    </Container>
  );
}
