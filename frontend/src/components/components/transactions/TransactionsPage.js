import { setModal, setDate } from "Reducers/mainReducer";
import { useSelector, useDispatch } from "react-redux";
import TransactionsList from "./TransactionsList";
import { useNavigate } from "react-router-dom";
import { MODAL_PAGES } from "Constants";
import pageIcon from "Assets/page.png";
import React from "react";

function TransactionsPage() {
  const transactions = useSelector((state) => state.main.transactions);
  const addresses = useSelector((state) => state.main.addresses);
  const shops = useSelector((state) => state.main.shops);
  const date = useSelector((state) => state.main.date);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const monthly = transactions.filter(
    (t) => t.date.replace(/\d+$/, "01") === date.replace(/\d+$/, "01")
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
      <h3 style={{ textAlign: "center" }}>No expenses in this month</h3>
    ) : (
      <h3 style={{ textAlign: "center" }}>Month expenses: {monthExpenses}</h3>
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
        <MontExpenses />
        <div
          style={{
            minHeight: "300px",
            margin: "2rem 0",
          }}
        >
          {Object.keys(dailyByShops).map((d) => (
            <React.Fragment key={d}>
              <h2 style={{ textAlign: "center" }}>
                {addresses.find((a) => a.id == d).local_name}
              </h2>
              <TransactionsList list={dailyByShops[d]} />
            </React.Fragment>
          ))}
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
