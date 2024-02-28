import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { updateState } from "Reducers/mainReducer";
import { useDispatch } from "react-redux";
import classnames from "classnames/bind";
import { API_URLS } from "Constants";
import style from "./style.scss";
import React from "react";
import axios from "axios";

import {
  CreateTransactionPage,
  CreateCategoryPage,
  TransactionsPage,
} from "./components";

const router = createBrowserRouter([
  {
    path: "/",
    element: <TransactionsPage />,
  },
  {
    path: "/create/category",
    element: <CreateCategoryPage />,
  },
  {
    path: "/create/transaction",
    element: <CreateTransactionPage />,
  },
]);

const cx = classnames.bind(style);

function App() {
  const dispatch = useDispatch();

  React.useEffect((_) => {
    Promise.all([
      axios.get(`${API_URLS.sub_category}`),
      axios.get(`${API_URLS.transaction}`),
      axios.get(`${API_URLS.category}`),
      axios.get(`${API_URLS.product}`),
      axios.get(`${API_URLS.address}`),
      axios.get(`${API_URLS.shop}`),
    ])
      .then((data) => {
        const [
          subCategories,
          transactions,
          categories,
          products,
          addresses,
          shops,
        ] = data;
        const product =
          products.data.find((p) => p.id == localStorage.getItem("product")) ||
          products.data?.[0] ||
          null;
        const shop =
          shops.data.find((s) => s.id == localStorage.getItem("shop")) ||
          shops.data?.[0] ||
          null;
        dispatch(
          updateState({
            subCategories: subCategories.data,
            transactions: transactions.data,
            categories: categories.data,
            addresses: addresses.data,
            products: products.data,
            shops: shops.data,
            product,
            shop,
          })
        );
      })
      .catch((e) => console.log(e));
  }, []);

  return (
    <React.Fragment>
      <RouterProvider router={router} />
    </React.Fragment>
  );
}

export default App;
