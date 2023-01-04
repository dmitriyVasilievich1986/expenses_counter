import { setModal, setDate } from "Reducers/mainReducer";
import { useSelector, useDispatch } from "react-redux";
import Transaction from "./Transaction";
import { MODAL_PAGES } from "Constants";
import pageIcon from "./page.png";
import React from "react";

function TransactionsList() {
  const transactions = useSelector((state) => state.main.transactions);
  const date = useSelector((state) => state.main.date);
  const dispatch = useDispatch();

  const monthly = transactions.filter(
    (t) => t.date.replace(/\d+$/, "01") === date.replace(/\d+$/, "01")
  );
  const daily = monthly.filter((t) => t.date === date);

  const Summary = (_) => {
    if (daily.length === 0) return null;
    return (
      <React.Fragment>
        <div
          style={{
            display: "flex",
            width: "100%",
            alignItems: "center",
            marginTop: "10px",
          }}
        >
          <div style={{ fontSize: "20px", fontWeight: "bold", flex: "3" }} />
          <div
            style={{
              width: "80px",
              textAlign: "center",
              fontWeight: "bold",
              fontSize: "18px",
              borderTop: "2px solid black",
            }}
          >
            {daily.reduce((sum, trans) => sum + +trans.price, 0).toFixed(2)}
          </div>
          <div style={{ width: "15px" }} />
        </div>
      </React.Fragment>
    );
  };

  return (
    <div style={{ display: "flex", justifyContent: "center" }}>
      <div style={{ width: "500px", marginTop: "5rem" }}>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <input
            onChange={(e) => dispatch(setDate(e.target.value))}
            value={String(date)}
            type="date"
          />
        </div>
        <h3 style={{ textAlign: "center" }}>
          Month expenses:{" "}
          {monthly.reduce((sum, trans) => sum + +trans.price, 0).toFixed(2)}
        </h3>
        <div
          style={{
            minHeight: "300px",
            margin: "2rem 0",
          }}
        >
          {daily.map((t) => (
            <Transaction
              transactionID={t.id}
              product={t.product}
              price={t.price}
              key={t.id}
            />
          ))}
          <Summary />
          <div
            style={{
              display: "flex",
              marginTop: "2rem",
              justifyContent: "space-around",
            }}
          >
            <div />
            <img
              style={{ width: "30px", height: "30px", cursor: "pointer" }}
              onClick={(_) => dispatch(setModal(MODAL_PAGES.newProductPage))}
              src={pageIcon}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default TransactionsList;
