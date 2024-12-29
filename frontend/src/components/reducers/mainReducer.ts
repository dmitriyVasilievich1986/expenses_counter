import { messageType } from "../components/alert/types";
import { createSlice } from "@reduxjs/toolkit";
import { mainStateOptionalType, mainStateType } from "./types";

const initialState: mainStateType = {
  isLoading: true,
  categories: [],
  addresses: [],
  products: [],
  message: null,
};

export const mainSlice = createSlice({
  name: "main",
  initialState: initialState,
  reducers: {
    setMessage: (state, action: { payload: messageType | null }) => {
      state.message = action.payload;
    },
    setIsLoading: (state, action: { payload: boolean }) => {
      state.isLoading = action.payload;
    },
    updateState: (state, action: { payload: mainStateOptionalType }) => {
      return {
        ...state,
        ...action.payload,
      };
    },
  },
});

export const { setIsLoading, updateState, setMessage } = mainSlice.actions;

export default mainSlice.reducer;
