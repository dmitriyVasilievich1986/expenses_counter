import { useSelector, useDispatch } from "react-redux";
import { updateState } from "Reducers/mainReducer";
import { MODAL_PAGES } from "Constants";
import trashIcon from "./trash.png";
import React from "react";

function Transaction(props) {
  const products = useSelector((state) => state.main.products);
  const dispatch = useDispatch();

  const product = products.find((p) => p.id === props.product);
  const { price, transactionID } = props;

  const clickHandler = (_) => {
    dispatch(
      updateState({
        modal: MODAL_PAGES.deletePage,
        deleteConfirm: transactionID,
      })
    );
  };

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        alignItems: "center",
        marginTop: "10px",
      }}
    >
      <div style={{ fontSize: "20px", fontWeight: "bold", flex: "3" }}>
        {product.name}
      </div>
      <div style={{ width: "80px", textAlign: "center" }}>{price}</div>
      <img
        style={{ width: "15px", height: "15px", cursor: "pointer" }}
        onClick={clickHandler}
        src={trashIcon}
      />
    </div>
  );
}

export default Transaction;
