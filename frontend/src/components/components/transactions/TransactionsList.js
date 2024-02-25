import Transaction from "./Transaction";
import React from "react";

function TransactionsList(props) {
  return (
    <React.Fragment>
      {props.list.map((t) => (
        <Transaction
          transactionID={t.id}
          product={t.product}
          price={t.price}
          count={t.count}
          key={t.id}
        />
      ))}
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
            width: "150px",
            textAlign: "center",
            fontWeight: "bold",
            fontSize: "18px",
            borderTop: "2px solid black",
          }}
        >
          {props.list
            .reduce((sum, trans) => sum + trans.price * trans.count, 0)
            .toFixed(2)}
        </div>
        <div style={{ width: "15px" }} />
      </div>
    </React.Fragment>
  );
}

export default TransactionsList;
