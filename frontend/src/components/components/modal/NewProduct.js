import { useSelector, useDispatch } from "react-redux";
import { updateState } from "Reducers/mainReducer";
import Select from "../../Select/Select";
import { API_URLS } from "Constants";
import axios from "axios";
import React from "react";

function NewProduct() {
  const subCategories = useSelector((state) => state.main.subCategories);
  const transactions = useSelector((state) => state.main.transactions);
  const subCategory = useSelector((state) => state.main.subCategory);
  const products = useSelector((state) => state.main.products);
  const product = useSelector((state) => state.main.product);
  const shops = useSelector((state) => state.main.shops);
  const shop = useSelector((state) => state.main.shop);
  const date = useSelector((state) => state.main.date);
  const [price, setPrice] = React.useState(100.99);
  const dispatch = useDispatch();

  const clickHandler = (_) => {
    const newItem = {
      sub_category: subCategory.id,
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
    <div>
      <Select
        changeHandler={(newItem) => dispatch(updateState({ shop: newItem }))}
        items={shops}
        value={shop}
      />
      <Select
        changeHandler={(newItem) =>
          dispatch(updateState({ subCategory: newItem }))
        }
        items={subCategories}
        value={subCategory}
      />
      <Select
        changeHandler={(newItem) => dispatch(updateState({ product: newItem }))}
        items={products}
        value={product}
      />
      <div>
        Price:{" "}
        <input
          onChange={(e) => setPrice(e.target.value)}
          value={price}
          type="number"
        />
      </div>
      <button onClick={clickHandler}>Save</button>
    </div>
  );
}

export default NewProduct;
