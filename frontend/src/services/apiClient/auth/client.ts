import axios from 'axios';

import type { LoginResponse } from './types';

export const useAuthAPIClient = () => {
  return {
    login: async (username: string, password: string) => {
      const response = await axios.post<LoginResponse>(
        `${import.meta.env.VITE_API_HOST}/api/login`,
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
