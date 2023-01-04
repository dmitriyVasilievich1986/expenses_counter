import { TransactionsList, ModalPage } from "./components";
import { updateState } from "Reducers/mainReducer";
import { useDispatch } from "react-redux";
import React from "react";
import axios from "axios";

const apiAddress = "/expenses/";

function App() {
  const dispatch = useDispatch();

  React.useEffect((_) => {
    Promise.all([
      axios.get(`${apiAddress}sub_category/`),
      axios.get(`${apiAddress}transaction/`),
      axios.get(`${apiAddress}product/`),
      axios.get(`${apiAddress}shop/`),
    ])
      .then((data) => {
        const [subCategories, transactions, products, shops] = data;
        dispatch(
          updateState({
            subCategory: subCategories?.data[0] || null,
            product: products.data?.[0] || null,
            shop: shops.data?.[0] || null,
            subCategories: subCategories.data,
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
      <TransactionsList />
    </div>
  );
}

export default App;
