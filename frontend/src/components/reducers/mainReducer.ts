import { TransactionTypeNumber } from "../pages/transactionsPage/types";
import { ProductTypeDetailed } from "../pages/productsPage/types";
import { CategoryTypeNumber } from "../pages/categoryPage/types";
import { mainStateOptionalType, mainStateType } from "./types";
import { messageType } from "../components/alert/types";
import { createSlice } from "@reduxjs/toolkit";
import {
  ShopAddressTypeNumber,
  ShopTypeNumber,
} from "../pages/shopsPage/types";

const initialState: mainStateType = {
  isLoading: false,
  transactions: [],
  categories: [],
  addresses: [],
  products: [],
  shops: [],
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
    updateShop: (state, action: { payload: ShopTypeNumber }) => {
      state.shops = state.shops.map((s) =>
        s.id === action.payload.id ? action.payload : s,
      );
    },
    setShops: (state, action: { payload: ShopTypeNumber[] }) => {
      state.shops = action.payload;
    },
    addShops: (state, action: { payload: ShopTypeNumber[] }) => {
      state.shops = [...state.shops, ...action.payload];
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
    setAddresses: (state, action: { payload: ShopAddressTypeNumber[] }) => {
      state.addresses = action.payload;
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
    setCategories: (state, action: { payload: CategoryTypeNumber[] }) => {
      state.categories = action.payload;
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
  setCategories,
  updateProduct,
  addProducts,
  updateAddress,
  addAddresses,
  setAddresses,
  updateShop,
  setShops,
  addShops,
  setIsLoading,
  updateState,
  setMessage,
} = mainSlice.actions;

export default mainSlice.reducer;
