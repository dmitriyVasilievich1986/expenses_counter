import { useSelector, useDispatch } from "react-redux";
import { updateState } from "Reducers/mainReducer";
import Select from "../../Select/Select";
import { API_URLS } from "Constants";
import axios from "axios";
import React from "react";

function NewProduct() {
  const transactions = useSelector((state) => state.main.transactions);
  const products = useSelector((state) => state.main.products);
  const product = useSelector((state) => state.main.product);
  const shops = useSelector((state) => state.main.shops);
  const shop = useSelector((state) => state.main.shop);
  const date = useSelector((state) => state.main.date);
  const [price, setPrice] = React.useState(100.99);
  const dispatch = useDispatch();

  const clickHandler = (_) => {
    const newItem = {
      product: product.id,
      date: String(date),
      shop: shop.id,
      price: price,
    };
    axios
      .post(`${API_URLS.transaction}`, newItem)
      .then((data) => {
        dispatch(
          updateState({
            transactions: [...transactions, data.data],
            modal: null,
          })
        );
      })
      .catch((e) => console.log(e));
  };

  if (product === null) return null;
  return (
    <div style={{ width: "500px", height: "200px", padding: "4rem" }}>
      <div style={{ marginTop: "1rem" }}>
        <Select
          changeHandler={(newItem) => dispatch(updateState({ shop: newItem }))}
          items={shops}
          value={shop}
        />
      </div>
      <div style={{ marginTop: "1rem" }}>
        <Select
          changeHandler={(newItem) =>
            dispatch(updateState({ product: newItem }))
          }
          items={products}
          value={product}
        />
      </div>
      <div style={{ marginTop: "1rem" }}>
        Price:{" "}
        <input
          onChange={(e) => setPrice(e.target.value)}
          value={price}
          type="number"
        />
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <button
          style={{ width: "150px", height: "35px", marginTop: "3rem" }}
          onClick={clickHandler}
        >
          Save
        </button>
      </div>
    </div>
  );
}

export default NewProduct;
