import { useSelector, useDispatch } from "react-redux";
import TransactionsList from "./TransactionsList";
import { setDate } from "Reducers/mainReducer";
import { useNavigate } from "react-router-dom";
import noPhotoIcon from "Assets/no-photo.png";
import classnames from "classnames/bind";
import pageIcon from "Assets/page.png";
import style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

function Shop(props) {
  const addresses = useSelector((state) => state.main.addresses);
  const shops = useSelector((state) => state.main.shops);

  const addres = addresses.find((a) => a.id == props.addresId);
  const shop = shops.find((s) => s.id == addres.shop);

  return (
    <div className={cx("shop-addres")}>
      <h2>
        <img
          src={shop.icon}
          onError={(t) => {
            t.target.src = noPhotoIcon;
            t.target.onError = null;
          }}
        />
        "{addres.local_name}" ({addres.address})
      </h2>
    </div>
  );
}

function TransactionsPage() {
  const transactions = useSelector((state) => state.main.transactions);
  const date = useSelector((state) => state.main.date);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const monthly = transactions.filter(
    (t) => t.date.replace(/\d+$/, "01") === date.replace(/\d+$/, "01"),
  );
  const dailyByShops = {};
  monthly.map((t) => {
    if (t.date === date) {
      if (t.address in dailyByShops) {
        dailyByShops[t.address].push(t);
      } else {
        dailyByShops[t.address] = [t];
      }
    }
  });

  const MontExpenses = () => {
    const monthExpenses = monthly
      .reduce((sum, trans) => sum + trans.price * trans.count, 0)
      .toFixed(2);
    return monthExpenses == 0 ? (
      <h3>No expenses in this month</h3>
    ) : (
      <h3>Month expenses: {monthExpenses}</h3>
    );
  };

  return (
    <div className={cx("transaction-container")}>
      <div className={cx("wrapper")}>
        <div className={cx("date")}>
          <input
            onChange={(e) => dispatch(setDate(e.target.value))}
            value={String(date)}
            type="date"
          />
        </div>
        <MontExpenses />
        <div className={cx("list")}>
          {Object.keys(dailyByShops).map((d) => (
            <React.Fragment key={d}>
              <Shop addresId={d} />
              <TransactionsList list={dailyByShops[d]} />
            </React.Fragment>
          ))}
          <div className={cx("create-button")}>
            <img
              onClick={(_) => navigate("/create/transaction")}
              src={pageIcon}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default TransactionsPage;
