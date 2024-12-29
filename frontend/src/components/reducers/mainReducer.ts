import { TransactionTypeNumber } from "../pages/transactionsPage/types";
import { ProductTypeDetailed } from "../pages/productsPage/types";
import { CategoryTypeNumber } from "../pages/categoryPage/types";
import { ShopAddressTypeNumber } from "../pages/shopsPage/types";
import { mainStateOptionalType, mainStateType } from "./types";
import { messageType } from "../components/alert/types";
import { createSlice } from "@reduxjs/toolkit";

const initialState: mainStateType = {
  isLoading: false,
  transactions: [],
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
    updateProduct: (state, action: { payload: ProductTypeDetailed }) => {
      state.products = state.products.map((p) =>
        p.id === action.payload.id ? action.payload : p,
      );
    },
    addProducts: (state, action: { payload: ProductTypeDetailed[] }) => {
      state.products = [...state.products, ...action.payload];
    },
    updateAddress: (state, action: { payload: ShopAddressTypeNumber }) => {
      state.addresses = state.addresses.map((a) =>
        a.id === action.payload.id ? action.payload : a,
      );
    },
    addAddresses: (state, action: { payload: ShopAddressTypeNumber[] }) => {
      state.addresses = [...state.addresses, ...action.payload];
    },
    updateCategoriy: (state, action: { payload: CategoryTypeNumber }) => {
      state.categories = state.categories.map((c) =>
        c.id === action.payload.id ? action.payload : c,
      );
    },
    addCategories: (state, action: { payload: CategoryTypeNumber[] }) => {
      state.categories = [...state.categories, ...action.payload];
    },
    updateTransaction: (state, action: { payload: TransactionTypeNumber }) => {
      state.transactions = state.transactions.map((t) =>
        t.id === action.payload.id ? action.payload : t,
      );
    },
    addTransactions: (state, action: { payload: TransactionTypeNumber[] }) => {
      state.transactions = [...state.transactions, ...action.payload];
    },
    setTransactions: (state, action: { payload: TransactionTypeNumber[] }) => {
      state.transactions = action.payload;
    },
    updateState: (state, action: { payload: mainStateOptionalType }) => {
      return {
        ...state,
        ...action.payload,
      };
    },
  },
});

export const {
  updateTransaction,
  addTransactions,
  setTransactions,
  updateCategoriy,
  addCategories,
  updateProduct,
  addProducts,
  updateAddress,
  addAddresses,
  setIsLoading,
  updateState,
  setMessage,
} = mainSlice.actions;

export default mainSlice.reducer;
