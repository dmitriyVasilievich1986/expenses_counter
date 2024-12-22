import { BrowserRouter, Route, Routes } from "react-router-dom";
import { updateState } from "Reducers/mainReducer";
import { useDispatch } from "react-redux";
import { API_URLS } from "Constants";
import React from "react";
import axios from "axios";

import { Navbar, Alert } from "./components";

import { ProductsPage, CategoryPage, ShopsPage } from "./pages";

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
          }),
        );
      })
      .catch((e) => console.log(e));
  }, []);

  return (
    <React.Fragment>
      <Alert />
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/create">
            <Route path="category">
              <Route path="" element={<CategoryPage />} />
              <Route path=":categoryId" element={<CategoryPage />} />
            </Route>

            <Route path="product">
              <Route path="" element={<ProductsPage />} />
              <Route path=":productId" element={<ProductsPage />} />
            </Route>

            <Route path="shop">
              <Route path="" element={<ShopsPage />} />
              <Route path=":shopId">
                <Route path="" element={<ShopsPage />} />
                <Route path="address/:addressId" element={<ShopsPage />} />
              </Route>
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </React.Fragment>
  );
}

export default App;
