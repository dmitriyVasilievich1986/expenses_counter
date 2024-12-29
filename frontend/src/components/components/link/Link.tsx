import { NavLink, useSearchParams } from "react-router-dom";
import classnames from "classnames/bind";
import React from "react";

import { PagesURLs } from "../../Constants";
import { UrlParamsType } from "./types";
import Box from "@mui/material/Box";
import style from "./style.scss";

const cx = classnames.bind(style);

export class Params implements UrlParamsType {
  address?: string | null = undefined;
  currentDate?: string | null = undefined;
  searchParams: URLSearchParams;

  constructor(params?: UrlParamsType) {
    this.searchParams = useSearchParams()[0];

    if (params?.currentDate === undefined)
      this.currentDate = this.searchParams.get("currentDate");
    else this.currentDate = params.currentDate;

    if (params?.address === undefined)
      this.address = this.searchParams.get("address");
    else this.address = params.address;
  }

  updateCurrentDate(currentDate?: string | null) {
    if (currentDate === undefined)
      this.currentDate = this.searchParams.get("currentDate");
    else this.currentDate = currentDate;
  }

  updateAddress(address?: string | null) {
    if (address === undefined) this.address = this.searchParams.get("address");
    else this.address = address;
  }

  update(params?: UrlParamsType) {
    this.updateCurrentDate(params?.currentDate);
    this.updateAddress(params?.address);
  }

  toString() {
    const filteredParams = Object.fromEntries(
      Object.entries(this).filter(([k, v]) => !!v && k !== "searchParams"),
    );
    const params = new URLSearchParams(filteredParams).toString();
    return params ? `?${params}` : "";
  }
}

export function Link(props: {
  to: PagesURLs | string;
  params?: UrlParamsType;
  children: React.ReactNode;
  className?: "prime" | "secondary";
  showActive?: boolean;
  Ref?: React.Ref<HTMLAnchorElement>;
}) {
  return (
    <NavLink
      ref={props.Ref}
      className={({ isActive }) =>
        cx(props.className ?? "prime", {
          isActive: isActive && props.showActive,
        })
      }
      to={{ pathname: props.to, search: new Params(props.params).toString() }}
    >
      {props.children}
    </NavLink>
  );
}

export function LinkBox(props: {
  to: PagesURLs | string;
  params?: UrlParamsType;
  children: React.ReactNode;
}) {
  const linkRef = React.useRef<HTMLAnchorElement>(null);

  const clickHandler = () => {
    if (linkRef.current) {
      linkRef.current.click();
    }
  };

  return (
    <Box onClick={clickHandler} className={cx("link-box")}>
      <Link {...props} Ref={linkRef} className="secondary">
        {props.children}
      </Link>
    </Box>
  );
}
