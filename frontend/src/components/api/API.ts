import { useDispatch } from "react-redux";
import axios from "axios";

import { setIsLoading, setMessage } from "../reducers/mainReducer";
import { APIResponseType, Methods, APIs } from "./types";
import { messageType } from "../components/alert/types";

export class API {
  dispatch: any;

  constructor() {
    this.dispatch = useDispatch();
  }

  send<R>(props: {
    url: APIs | string;
    onSuccess?: (data: any) => void;
    onFail?: () => void;
    data?: { [key in string]: any };
    successMessage?: messageType;
    method?: Methods;
  }) {
    this.dispatch(setIsLoading(true));
    axios({
      url: props.url,
      method: props?.method ?? Methods.get,
      data: props?.data,
    })
      .then((response: APIResponseType<R>) => {
        if (props?.successMessage) {
          this.dispatch(setMessage(props.successMessage));
        }
        if (props?.onSuccess) {
          props.onSuccess(response.data);
        }
      })
      .catch((e) => {
        console.log(e);
        this.dispatch(setMessage({ message: "Error", severity: "error" }));
        if (props?.onFail) {
          props.onFail();
        }
      })
      .finally(() => this.dispatch(setIsLoading(false)));
  }
}
