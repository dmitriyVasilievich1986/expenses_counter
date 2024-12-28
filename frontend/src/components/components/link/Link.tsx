import { NavLink, useSearchParams } from "react-router-dom";
import React from "react";

import { PagesURLs } from "../../Constants";
import { UrlParamsType } from "./types";

class Params implements UrlParamsType {
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
  className?: string;
}) {
  return (
    <NavLink
      className={props.className}
      to={{ pathname: props.to, search: new Params(props.params).toString() }}
    >
      {props.children}
    </NavLink>
  );
}
