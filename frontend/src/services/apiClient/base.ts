import axios from 'axios';
import Cookies from 'js-cookie';

import { useMainStore } from '@store/main';

export const apiClientInstance = axios.create({
  baseURL: import.meta.env.VITE_API_HOST ?? '',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - set auth token
apiClientInstance.interceptors.request.use((config) => {
  const accessToken = Cookies.get('accessToken');

  if (!accessToken) {
    const fullRedirectUrl = `/login?redirectTo=${encodeURIComponent(window.location.pathname)}`;
    window.location.href = fullRedirectUrl;
    throw new Error('Unauthorized');
  }

  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  return config;
});

export const useApiClientWrapper = () => {
  const setIsLoading = useMainStore((state) => state.setIsLoading);

  return {
    wrapper: async <T>(func: () => Promise<T>): Promise<T> => {
      try {
        setIsLoading(true);
        const response = await func();
        return response;
      } catch (error) {
        console.error('Error:', error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
  };
};
