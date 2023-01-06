import { ModalPage, TransactionsPage } from "./components";
import { updateState } from "Reducers/mainReducer";
import { useDispatch } from "react-redux";
import { API_URLS } from "Constants";
import React from "react";
import axios from "axios";

function App() {
  const dispatch = useDispatch();

  React.useEffect((_) => {
    Promise.all([
      axios.get(`${API_URLS.transaction}`),
      axios.get(`${API_URLS.product}`),
      axios.get(`${API_URLS.shop}`),
    ])
      .then((data) => {
        const [transactions, products, shops] = data;
        dispatch(
          updateState({
            product: products.data?.[0] || null,
            shop: shops.data?.[0] || null,
            transactions: transactions.data,
            products: products.data,
            shops: shops.data,
          })
        );
      })
      .catch((e) => console.log(e));
  }, []);

  return (
    <div>
      <ModalPage />
      <TransactionsPage />
    </div>
  );
}

export default App;
