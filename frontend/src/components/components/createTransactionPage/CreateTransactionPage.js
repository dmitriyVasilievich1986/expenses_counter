import { updateState, setDate } from "Reducers/mainReducer";
import CategorySelect from "../categorySelect";
import classnames from "classnames/bind";
import { connect } from "react-redux";
import localStyle from "./style.scss";
import { API_URLS } from "Constants";
import axios from "axios";
import React from "react";

const cx = classnames.bind(localStyle);

function CreateTransactionPage(props) {
  if (!props.addresses.length || !props.products.length || !props.transactions)
    return null;

  const [product, setProduct] = React.useState(0);
  const [price, setPrice] = React.useState(0);
  const [count, setCount] = React.useState(0);
  const [shop, setShop] = React.useState(0);

  const getProductCategories = () => {
    return Object.fromEntries(
      props.subCategories.map((sc) => [
        sc.name,
        props.products
          .filter((p) => p.sub_category === sc.id)
          .map((p) => ({ ...p, label: p.name })),
      ])
    );
  };
  const getProductNames = () => {
    return props.products.map((p) => ({ ...p, label: p.name }));
  };
  const getProductObjects = () => {
    return {
      names: getProductNames(),
      categories: getProductCategories(),
    };
  };

  const getShopsNames = () => {
    const allShops = [...new Set(props.addresses.map((a) => a.shop))];

    return Object.fromEntries(
      props.shops
        .filter((s) => allShops.includes(s.id))
        .map((s) => [
          s.name,
          props.addresses
            .filter((a) => a.shop === s.id)
            .map((a) => ({ ...a, label: a.local_name })),
        ])
    );
  };
  const getShopsCategories = () => {
    const allCategories = [...new Set(props.shops.map((s) => s.sub_category))];

    return Object.fromEntries(
      props.subCategories
        .filter((sc) => allCategories.includes(sc.id))
        .map((sc) => [
          sc.name,
          props.addresses
            .filter((a) =>
              props.shops
                .filter((s) => s.sub_category === sc.id)
                .map((s) => s.id)
                .includes(a.shop)
            )
            .map((a) => ({ ...a, label: a.local_name })),
        ])
    );
  };
  const getShopsAddresses = () => {
    return props.addresses.map((a) => ({ ...a, label: a.address }));
  };
  const getShopsObjects = () => {
    return {
      names: getShopsNames(),
      addresses: getShopsAddresses(),
      categories: getShopsCategories(),
    };
  };

  const submitHandler = (e) => {
    e.preventDefault();

    const newItem = {
      product: props.products[product].id,
      address: props.addresses[shop].id,
      date: String(props.date),
      price,
      count,
    };
    axios
      .post(`${API_URLS.transaction}`, newItem)
      .then((data) => {
        props.updateState({
          transactions: [...props.transactions, data.data],
        });
      })
      .catch((e) => console.log(e));
  };

  const todaysTransactions = props.transactions.filter(
    (t) => t.date === props.date
  );

  return (
    <div className={cx("wrapper")}>
      <div className={cx("left")}>
        <div>
          <label>Today's transactions:</label>
          <ul>
            {todaysTransactions.length > 0 ? (
              todaysTransactions.map((t) => (
                <li key={t.id}>
                  {t.price} x {t.count}
                </li>
              ))
            ) : (
              <li>no transactions</li>
            )}
            <li>
              <div className={cx("row")}>
                <div className={cx("summary")}>
                  {price} x {count}
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
      <div className={cx("center")}>
        <form onSubmit={submitHandler}>
          <div className={cx("date")}>
            <input
              type="date"
              value={props.date}
              onChange={(e) => props.setDate(e.target.value)}
            />
          </div>
          <div className={cx("row")}>
            <label>Product:</label>
            <CategorySelect
              value={props.products[product].name}
              onClick={(np) =>
                setProduct(props.products.map((p) => p.id).indexOf(np.id))
              }
              objects={getProductObjects()}
            />
          </div>
          <div className={cx("row")}>
            <label>Shop:</label>
            <CategorySelect
              onClick={(na) =>
                setShop(props.addresses.map((a) => a.id).indexOf(na.id))
              }
              value={props.shops[shop].name}
              objects={getShopsObjects()}
            />
          </div>
          <div className={cx("row")}>
            <label>Price:</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
            />
          </div>
          <div className={cx("row")}>
            <label>Count:</label>
            <input
              type="number"
              value={count}
              onChange={(e) => setCount(e.target.value)}
            />
          </div>
          <div className={cx("row")}>
            <label>Summary:</label>
            <div className={cx("summary")}>
              {Math.round(price * count * 100) / 100}
            </div>
          </div>
          <div className={cx("save-button")}>
            <button onClick={submitHandler}>save</button>
          </div>
        </form>
      </div>
      <div className={cx("left")} />
    </div>
  );
}

const mapStateToProps = (state) => ({
  subCategories: state.main.subCategories,
  transactions: state.main.transactions,
  categories: state.main.categories,
  addresses: state.main.addresses,
  products: state.main.products,
  product: state.main.product,
  shops: state.main.shops,
  date: state.main.date,
});

export default connect(mapStateToProps, { updateState, setDate })(
  CreateTransactionPage
);
