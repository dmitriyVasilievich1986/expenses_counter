import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  date: localStorage.getItem("date") || new Date().toISOString().split("T")[0],
  price: localStorage.getItem("price") || 0,
  deleteConfirm: null,
  isLoading: true,
  modal: null,
  subCategories: [],
  transactions: [],
  categories: [],
  addresses: [],
  products: [],
  shops: [],
  transaction: null,
  product: null,
  shop: null,
  message: null,
};

export const mainSlice = createSlice({
  name: "main",
  initialState: initialState,
  reducers: {
    setDate: (state, action) => {
      localStorage.setItem("date", action.payload);
      state.date = action.payload;
    },
    setModal: (state, action) => {
      state.modal = action.payload;
    },
    setPrice: (state, action) => {
      localStorage.setItem("price", action.payload);
      state.price = action.payload;
    },
    setShop: (state, action) => {
      localStorage.setItem("shop", action.payload.id);
      state.shop = action.payload;
    },
    setProduct: (state, action) => {
      localStorage.setItem("product", action.payload.id);
      state.product = action.payload;
    },
    updateState: (state, action) => {
      return {
        ...state,
        ...action.payload,
      };
    },
  },
});

export const { updateState, setDate, setModal, setShop, setProduct, setPrice } =
  mainSlice.actions;

export default mainSlice.reducer;
