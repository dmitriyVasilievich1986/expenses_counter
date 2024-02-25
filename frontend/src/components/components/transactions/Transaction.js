import { useSelector, useDispatch } from "react-redux";
import { updateState } from "Reducers/mainReducer";
import classnames from "classnames/bind";
import { MODAL_PAGES } from "Constants";
import binIcon from "Assets/bin.png";
import style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

function Transaction(props) {
  const products = useSelector((state) => state.main.products);
  const dispatch = useDispatch();

  const product = products.find((p) => p.id === props.product);
  const { count, price, transactionID } = props;

  const clickHandler = (_) => {
    dispatch(
      updateState({
        modal: MODAL_PAGES.deletePage,
        deleteConfirm: transactionID,
      })
    );
  };

  return (
    <div className={cx("transaction")}>
      <div className={cx("name")}>{product.name}</div>
      <div className={cx("price")}>
        {price} x {count}
      </div>
      <img onClick={clickHandler} src={binIcon} />
    </div>
  );
}

export default Transaction;
