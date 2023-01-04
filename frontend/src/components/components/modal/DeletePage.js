import { useSelector, useDispatch } from "react-redux";
import { updateState } from "Reducers/mainReducer";
import { API_URLS, DELETE } from "Constants";
import axios from "axios";
import React from "react";

function DeletePage() {
  const [deleteValue, setDeleteValue] = React.useState("");

  const deleteConfirm = useSelector((state) => state.main.deleteConfirm);
  const transactions = useSelector((state) => state.main.transactions);
  const dispatch = useDispatch();

  const clickHandler = (_) => {
    if (deleteValue === DELETE) {
      axios
        .delete(`${API_URLS.transaction}${deleteConfirm}/`)
        .then((_) => {
          dispatch(
            updateState({
              transactions: transactions.filter((t) => t.id !== deleteConfirm),
              deleteConfirm: null,
              modal: null,
            })
          );
        })
        .catch((e) => console.log(e));
    }
  };

  return (
    <div style={{ width: "500px", height: "150px", padding: "4rem" }}>
      <div>Write "{DELETE}" to delete transaction.</div>
      <div>
        <input
          onChange={(e) => setDeleteValue(e.target.value)}
          style={{ margin: "1rem 0" }}
          placeholder={DELETE}
          value={deleteValue}
          type="text"
        />
      </div>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <button
          style={{ width: "150px", height: "35px", marginTop: "3rem" }}
          disabled={deleteValue !== DELETE}
          onClick={clickHandler}
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default DeletePage;
