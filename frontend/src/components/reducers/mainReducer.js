import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  isLoading: true,
  subCategories: [],
  transactions: [],
  products: [],
  shops: [],
  subCategory: null,
  transaction: null,
  product: null,
  shop: null,
};

export const mainSlice = createSlice({
  name: "main",
  initialState: initialState,
  reducers: {
    updateState: (state, action) => {
      return {
        ...state,
        ...action.payload,
      };
    },
  },
});

export const { updateState } = mainSlice.actions;

export default mainSlice.reducer;
