import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

import type { MainStoreStateType } from './types';

export const useMainStore = create<MainStoreStateType>()(
  devtools((set) => ({
    isLoading: false,
    setIsLoading: (isLoading) => set({ isLoading }, undefined, 'setIsLoading'),
  }))
);
