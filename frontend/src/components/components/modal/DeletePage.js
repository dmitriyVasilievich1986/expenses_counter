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
    <div>
      <div>Write "{DELETE}" to delete transaction.</div>
      <div>
        <input
          onChange={(e) => setDeleteValue(e.target.value)}
          value={deleteValue}
          type="text"
        />
      </div>
      <button onClick={clickHandler}>Delete</button>
    </div>
  );
}

export default DeletePage;
