import { NavLink } from "react-router-dom";
import classnames from "classnames/bind";
import style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

function Navbar() {
  return (
    <div className={cx("navbar")}>
      <div className={cx("wrapper")}>
        <NavLink className={({ isActive }) => cx("link", { isActive })} to="/">
          Home
        </NavLink>
        <NavLink
          className={({ isActive }) => cx("link", { isActive })}
          to="/create/transaction"
        >
          Transactions
        </NavLink>
        <NavLink
          className={({ isActive }) => cx("link", { isActive })}
          to="/create/category"
        >
          Categories
        </NavLink>
        <NavLink
          className={({ isActive }) => cx("link", { isActive })}
          to="/create/shop"
        >
          Shops
        </NavLink>
      </div>
    </div>
  );
}

export default Navbar;
