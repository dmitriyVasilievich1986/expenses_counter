import { BrowserRouter, Route, Routes } from "react-router-dom";
import React from "react";

import { Navbar } from "./components/navbar/Navbar";
import { Alert } from "./components/alert/Alert";

import {
  TransactionsPage,
  ProductsPage,
  CategoryPage,
  ShopsPage,
} from "./pages";

function App() {
  return (
    <React.Fragment>
      <Alert />
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/create">
            <Route path="category" element={<CategoryPage />}>
              <Route path=":categoryId" element={<CategoryPage />} />
            </Route>

            <Route path="product" element={<ProductsPage />}>
              <Route path=":productId" element={<ProductsPage />} />
            </Route>

            <Route path="transaction" element={<TransactionsPage />}>
              <Route path=":transactionId" element={<TransactionsPage />} />
            </Route>

            <Route path="shop" element={<ShopsPage />}>
              <Route path=":shopId" element={<ShopsPage />}>
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
