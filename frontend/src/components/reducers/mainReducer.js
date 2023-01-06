import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  date: new Date().toISOString().split("T")[0],
  deleteConfirm: null,
  isLoading: true,
  modal: null,
  transactions: [],
  products: [],
  shops: [],
  transaction: null,
  product: null,
  shop: null,
};

export const mainSlice = createSlice({
  name: "main",
  initialState: initialState,
  reducers: {
    setDate: (state, action) => {
      state.date = action.payload;
    },
    setModal: (state, action) => {
      state.modal = action.payload;
    },
    updateState: (state, action) => {
      return {
        ...state,
        ...action.payload,
      };
    },
  },
});

export const { updateState, setDate, setModal } = mainSlice.actions;

export default mainSlice.reducer;
