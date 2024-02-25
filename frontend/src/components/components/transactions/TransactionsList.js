import classnames from "classnames/bind";
import Transaction from "./Transaction";
import style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

function TransactionsList(props) {
  return (
    <React.Fragment>
      {props.list.map((t) => (
        <Transaction {...t} key={t.id} />
      ))}
      <div className={cx("transaction")}>
        <div className={cx("name")} />
        <div className={cx("price", "bold")}>
          {props.list
            .reduce((sum, trans) => sum + trans.price * trans.count, 0)
            .toFixed(2)}
        </div>
      </div>
    </React.Fragment>
  );
}

export default TransactionsList;
