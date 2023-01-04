import { setModal, setDate } from "Reducers/mainReducer";
import { useSelector, useDispatch } from "react-redux";
import Transaction from "./Transaction";
import { MODAL_PAGES } from "Constants";
import React from "react";

function TransactionsList() {
  const transactions = useSelector((state) => state.main.transactions);
  const date = useSelector((state) => state.main.date);
  const dispatch = useDispatch();

  const monthly = transactions.filter(
    (t) => t.date.replace(/\d+$/, "01") === date.replace(/\d+$/, "01")
  );
  const daily = monthly.filter((t) => t.date === date);

  return (
    <div>
      <div>
        Date:{" "}
        <input
          onChange={(e) => dispatch(setDate(e.target.value))}
          value={String(date)}
          type="date"
        />
      </div>
      <div>
        Daily summary:{" "}
        {daily.reduce((sum, trans) => sum + +trans.price, 0).toFixed(2)}
      </div>
      <div>
        Monthly summary:{" "}
        {monthly.reduce((sum, trans) => sum + +trans.price, 0).toFixed(2)}
      </div>
      <div>
        {daily.map((t) => (
          <Transaction
            transactionID={t.id}
            product={t.product}
            price={t.price}
            key={t.id}
          />
        ))}
      </div>
      <button onClick={(_) => dispatch(setModal(MODAL_PAGES.newProductPage))}>
        New
      </button>
    </div>
  );
}

export default TransactionsList;
