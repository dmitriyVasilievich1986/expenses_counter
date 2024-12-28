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
        <Link to="/" showActive>
          Home
        </Link>
        <Link to={PagesURLs.Transaction} showActive>
          Transactions
        </Link>
        <Link to={PagesURLs.Category} showActive>
          Categories
        </Link>
        <Link to={PagesURLs.Shop} showActive>
          Shops
        </Link>
        <Link to={PagesURLs.Product} showActive>
          Products
        </Link>
      </div>
    </div>
  );
}
