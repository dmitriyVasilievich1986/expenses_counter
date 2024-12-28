import { PagesURLs } from "../../Constants";
import classnames from "classnames/bind";
import { Link } from "../link/Link";
import style from "./style.scss";
import React from "react";

const cx = classnames.bind(style);

export function Navbar() {
  return (
    <div className={cx("navbar")}>
      <div className={cx("wrapper")}>
        <Link className={({ isActive }) => cx("link", { isActive })} to="/">
          Home
        </Link>
        <Link
          className={({ isActive }) => cx("link", { isActive })}
          to={PagesURLs.Transaction}
        >
          Transactions
        </Link>
        <Link
          className={({ isActive }) => cx("link", { isActive })}
          to={PagesURLs.Category}
        >
          Categories
        </Link>
        <Link
          className={({ isActive }) => cx("link", { isActive })}
          to={PagesURLs.Shop}
        >
          Shops
        </Link>
        <Link
          className={({ isActive }) => cx("link", { isActive })}
          to={PagesURLs.Product}
        >
          Products
        </Link>
      </div>
    </div>
  );
}
