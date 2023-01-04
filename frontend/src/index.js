import { createRoot } from "react-dom/client";
import App from "./components/App";
import "./styles/style.scss";
import React from "react";

const container = document.getElementById("app");
const root = createRoot(container);
root.render(<App tab="home" />);