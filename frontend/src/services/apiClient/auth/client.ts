import axios from 'axios';

import type { LoginResponse } from './types';

export const useAuthAPIClient = () => {
  return {
    login: async (username: string, password: string) => {
      const apiHost = import.meta.env.VITE_API_HOST ?? '';
      const response = await axios.post<LoginResponse>(
        `${apiHost}/api/login`,
        {
          username,
          password,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      return response.data;
    },
  };
};
