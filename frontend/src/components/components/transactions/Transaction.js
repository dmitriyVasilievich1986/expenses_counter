import { useSelector, useDispatch } from "react-redux";
import { updateState } from "Reducers/mainReducer";
import React from "react";

function Transaction(props) {
  const products = useSelector((state) => state.main.products);
  const dispatch = useDispatch();

  const product = products.find((p) => p.id === props.product);
  const { price, transactionID } = props;

  const clickHandler = (_) => {
    dispatch(updateState({ modal: "Delete", deleteConfirm: transactionID }));
  };

  return (
    <div>
      {product.name}: {price}
      <button onClick={clickHandler}>Delete</button>
    </div>
  );
}

export default Transaction;
