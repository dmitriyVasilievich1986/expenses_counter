import { NavLink, useSearchParams } from "react-router-dom";
import classnames from "classnames/bind";
import React from "react";

import { PagesURLs } from "../../Constants";
import { UrlParamsType } from "./types";
import style from "./style.scss";

const cx = classnames.bind(style);

export class Params implements UrlParamsType {
  address?: string | null = undefined;
  currentDate?: string | null = undefined;

  constructor(params?: UrlParamsType) {
    const [searchParams] = useSearchParams();

    this.currentDate =
      params?.currentDate === null
        ? undefined
        : searchParams.get("currentDate");
    this.address =
      params?.address === null ? undefined : searchParams.get("address");
  }

  toString() {
    const filteredParams = Object.fromEntries(
      Object.entries(this).filter(([_, v]) => !!v),
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
}) {
  return (
    <NavLink
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
