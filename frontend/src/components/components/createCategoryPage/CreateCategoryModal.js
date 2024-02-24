import ModalContainer from "../modalContainer";
import classnames from "classnames/bind";
import localStyle from "./style.scss";
import { API_URLS } from "Constants";
import React from "react";
import axios from "axios";

const cx = classnames.bind(localStyle);

function InpurRow(props) {
  return (
    <div className={cx("row")}>
      <label>{props.label}:</label>
      <input
        type="text"
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        placeholder={props?.placeholder || props.label.toLowerCase()}
      />
    </div>
  );
}

function SaveButton(props) {
  const getButtonText = () => {
    switch (props.method) {
      case "post":
        return "save";
      case "put":
        return "update";
      default:
        return "delete";
    }
  };

  return (
    <div className={cx("save-button")}>
      <button>{getButtonText()}</button>
    </div>
  );
}

function CreateCategoryModal(props) {
  const [description, setDescription] = React.useState("");
  const [iconURL, setIconURL] = React.useState("");
  const [name, setName] = React.useState("");

  React.useEffect(() => {
    setDescription(props?.description || "");
    setIconURL(props?.iconURL || "");
    setName(props?.name || "");
  }, [props.name, props.description, props.iconURL]);

  const getData = () => {
    const data = props?.data || {};
    switch (props.url) {
      case API_URLS.address:
        return {
          ...data,
          address: name,
          local_name: description,
        };
      case API_URLS.shop:
        return { ...data, name, description, icon: iconURL };
      default:
        return { ...data, name, description };
    }
  };

  const submitHandler = (e) => {
    e.preventDefault();
    axios({ ...props.axiosParams, data: getData() })
      .then((data) => {
        props.submitHandler(data);
        props.closeHandler();
      })
      .catch((e) => console.log(e))
      .finally(() => {
        setDescription("");
        setIconURL("");
        setName("");
      });
  };

  if (props?.axiosParams?.method === "delete") {
    return (
      <ModalContainer closeHandler={props.closeHandler}>
        <div className={cx("container")}>
          <form onSubmit={submitHandler}>
            <h3>Are you sure to delete this?</h3>
            <SaveButton method={props.axiosParams.method} />
          </form>
        </div>
      </ModalContainer>
    );
  } else if (
    props?.url === API_URLS.sub_category ||
    props?.url === API_URLS.category ||
    props?.url === API_URLS.product
  ) {
    return (
      <ModalContainer closeHandler={props.closeHandler}>
        <div className={cx("container")}>
          <form onSubmit={submitHandler}>
            <InpurRow label="Name" value={name} onChange={setName} />
            <InpurRow
              onChange={setDescription}
              value={description}
              label="Description"
            />
            <SaveButton method={props.axiosParams.method} />
          </form>
        </div>
      </ModalContainer>
    );
  } else if (props?.url === API_URLS.shop) {
    return (
      <ModalContainer closeHandler={props.closeHandler}>
        <div className={cx("container")}>
          <form onSubmit={submitHandler}>
            <InpurRow label="Name" value={name} onChange={setName} />
            <InpurRow
              onChange={setDescription}
              value={description}
              label="Description"
            />
            <InpurRow label="Icon URL" value={iconURL} onChange={setIconURL} />
            <SaveButton method={props.axiosParams.method} />
          </form>
        </div>
      </ModalContainer>
    );
  } else if (props?.url === API_URLS.address) {
    return (
      <ModalContainer closeHandler={props.closeHandler}>
        <div className={cx("container")}>
          <form onSubmit={submitHandler}>
            <InpurRow label="Address" value={name} onChange={setName} />
            <InpurRow
              onChange={setDescription}
              value={description}
              label="Local name"
            />
            <SaveButton method={props.axiosParams.method} />
          </form>
        </div>
      </ModalContainer>
    );
  }
  return null;
}

export default CreateCategoryModal;
