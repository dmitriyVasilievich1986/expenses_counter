import { useMainStore } from '@store/main';
import axios from 'axios';

export const apiClientInstance = axios.create({
  baseURL: import.meta.env.VITE_API_HOST,
  headers: {
    'Content-Type': 'application/json',
  },
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
