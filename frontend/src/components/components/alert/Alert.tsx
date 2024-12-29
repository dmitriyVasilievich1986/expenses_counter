import { useDispatch, useSelector } from "react-redux";
import React from "react";

import { default as AlertBar } from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";

import { setMessage } from "../../reducers/mainReducer";
import { mainStateType } from "../../reducers/types";

export function Alert() {
  const message = useSelector(
    (state: { main: mainStateType }) => state.main.message,
  );
  const dispatch = useDispatch();

  return (
    <Snackbar
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      ClickAwayListenerProps={{ onClickAway: () => null }}
      onClose={(_) => dispatch(setMessage(null))}
      open={message !== null}
      autoHideDuration={3000}
    >
      <AlertBar severity={message?.severity || "success"} variant="filled">
        {message?.message}
      </AlertBar>
    </Snackbar>
  );
}
