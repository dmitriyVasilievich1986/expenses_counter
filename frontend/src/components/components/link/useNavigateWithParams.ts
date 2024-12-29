import { useNavigate } from "react-router-dom";

import { UrlParamsType } from "./types";
import { Params } from "./Link";

export function useNavigateWithParams() {
  const navigate = useNavigate();
  const params = new Params();

  return (to: string, newParams?: UrlParamsType) => {
    params.update(newParams);
    navigate(`${to}${params.toString()}`);
  };
}
