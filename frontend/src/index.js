import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import store from "./components/store";
import App from "./components/App";
import "./styles/style.scss";
import React from "react";

const container = document.getElementById("app");
const root = createRoot(container);
root.render(
  <Provider store={store}>
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <App tab="home" />
    </LocalizationProvider>
  </Provider>,
);
