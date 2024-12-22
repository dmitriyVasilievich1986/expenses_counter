import { useDispatch, useSelector } from "react-redux";
import React from "react";

import { default as AlertBar } from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";

import { updateState } from "../../reducers/mainReducer";

export function Alert() {
  const message = useSelector((state) => state.main.message);
  const dispatch = useDispatch();

  return (
    <Snackbar
      anchorOrigin={{ vertical: "bottom", horizontal: "right" }}
      onClose={(_) => dispatch(updateState({ message: null }))}
      open={message !== null}
      autoHideDuration={3000}
      message="Note archived"
    >
      <AlertBar severity={message?.severity || "success"} variant="filled">
        {message?.message}
      </AlertBar>
    </Snackbar>
  );
}
